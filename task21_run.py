#!/usr/bin/env python3
"""Task 21: no-Top-P one-hop 2^3 module ablation against frozen iKnow-05b."""
import os
os.environ['CUBLAS_WORKSPACE_CONFIG'] = ':4096:8'
os.environ['PYTHONHASHSEED'] = '42'

import argparse, hashlib, importlib.util, json, math, random
from collections import Counter
from pathlib import Path
import numpy as np
import torch
import torch.nn.functional as F
from tqdm import tqdm

ROOT = Path('/data/zkx/zkx/review1')
TASK = ROOT / '21_noTopP_factorial_vs_frozen_iKnow'
AAKV_SOURCE = ROOT / '20A_topP5_aligned_selector_exploration' / 'aakv_all.json'
METHODS = [
    'CLAP',
    'I_Frozen-iKnow-05b',
    'T_AAKV-only',
    'F_Fusion-only',
    'S_Selector-only',
    'TF_AAKV+Fusion',
    'TS_AAKV+Selector',
    'FS_Fusion+Selector',
    'TFS_AAKV+Fusion+Selector',
]

def seed_all(value):
    random.seed(value); np.random.seed(value % (2**32 - 1)); torch.manual_seed(value)
    torch.cuda.manual_seed_all(value)

def load_module(path):
    spec = importlib.util.spec_from_file_location('task21_runtime', str(path))
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module); return module

def nlse(values, kappa=100.0):
    return (torch.logsumexp(kappa * values, dim=0) - math.log(values.numel())) / kappa

def joint(base_value, evidence):
    if not evidence.numel(): return base_value
    return nlse(torch.cat((base_value.reshape(1), evidence.reshape(-1))))

def hierarchical(base_value, evidence):
    if not evidence.numel(): return base_value
    return 0.5 * base_value + 0.5 * nlse(evidence.reshape(-1))

def best_positive_rank(scores, truths):
    order = torch.argsort(scores, descending=True).cpu().numpy()
    return min(int(np.where(order == int(y))[0][0]) + 1 for y in truths)

def metrics(ranks):
    x = np.asarray(ranks, dtype=float)
    return {'Hit@1': float(100*np.mean(x <= 1)), 'Hit@3': float(100*np.mean(x <= 3)),
            'Hit@5': float(100*np.mean(x <= 5)), 'MRR': float(100*np.mean(1/x))}

def select_relation(relation_scores, relations):
    pred, margin = {}, {}
    for relation in relations:
        values = torch.topk(relation_scores[relation], k=min(2, relation_scores[relation].numel())).values
        pred[relation] = int(torch.argmax(relation_scores[relation]))
        margin[relation] = float(values[0] - values[1]) if values.numel() > 1 else 0.0
    votes = Counter(pred.values()); max_votes = max(votes.values())
    candidates = sorted(c for c, n in votes.items() if n == max_votes)
    consensus = max(candidates, key=lambda c: (sum(margin[r] for r in relations if pred[r] == c), -c))
    supporting = sorted((r for r in relations if pred[r] == consensus), key=lambda r: (-margin[r], r))
    return supporting[0], consensus, max_votes

def save_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')

def main(dataset):
    out = TASK / dataset; out.mkdir(parents=True, exist_ok=True)
    source = ROOT / '12_shared-abcd-statistics' / dataset
    runtime = load_module(source / 'frozen_inputs' / 'runtime.py'); device = runtime.DEVICE
    seed_all(42); torch.use_deterministic_algorithms(True)
    torch.backends.cudnn.benchmark = False; torch.backends.cudnn.deterministic = True
    torch.backends.cuda.matmul.allow_tf32 = False; torch.backends.cudnn.allow_tf32 = False

    clap = runtime.CLAP(version='2023', use_cuda=True); clap.clap.eval()
    samples = list(runtime.iter_samples(runtime.load_dataset()))
    frozen = torch.load(source / 'text_embeddings.pt', map_location='cpu')
    label_embeddings = frozen['labels'].to(device)
    frozen_evidence = frozen['evidence'].to(device); frozen_indices = frozen['indices']
    relation_cache = torch.load(ROOT / f'18a_relation_oracle_audit/{dataset}/results/static_relation_cache.pt', map_location='cpu')
    relations = relation_cache['relations']
    prompt_to_index = {text: i for i, text in enumerate(relation_cache['prompts'])}
    all_prompt_embeddings = relation_cache['prompt_embeddings'].to(device)
    aakv_texts = json.loads(AAKV_SOURCE.read_text(encoding='utf-8'))['texts']

    keys, seen = [], set(); relation_keys = {r: {} for r in relations}
    for relation in relations:
        for class_index, items in relation_cache['tails'][relation].items():
            ids = []
            for tail, prompt in items:
                head = prompt.split(', ', 1)[0]
                key = '\t'.join((head, relation, tail))
                if key not in seen: seen.add(key); keys.append(key)
                ids.append(key)
            relation_keys[relation][int(class_index)] = ids
    missing = [k for k in keys if k not in aakv_texts]
    if missing: raise RuntimeError(f'AAKV cache missing {len(missing)} keys; first={missing[0]}')
    key_to_index = {k: i for i, k in enumerate(keys)}
    chunks = []
    for start in range(0, len(keys), 128):
        text = [aakv_texts[k] for k in keys[start:start+128]]
        chunks.append(F.normalize(runtime.get_safe_text_embeddings(clap, text, device), dim=-1))
    aakv_embeddings = torch.cat(chunks, dim=0)

    ranks = {m: [] for m in METHODS}; rows, score_rows = [], []
    selected_counts = {name: Counter() for name in ('S', 'TS', 'FS', 'TFS')}
    for index, sample in enumerate(tqdm(samples, desc=dataset, mininterval=10)):
        sample_seed = int(hashlib.sha256(('42|' + sample['audio_path']).encode()).hexdigest()[:8], 16)
        seed_all(sample_seed)
        audio = torch.load(source / 'audio_cache' / f'{index:06d}.pt', map_location=device)
        base = (audio @ label_embeddings.T).squeeze(0)
        top_classes = torch.argsort(base, descending=True)[:5].tolist()
        aakv_similarity = (audio @ aakv_embeddings.T).squeeze(0)

        vectors = {'CLAP': base.clone()}
        i_vec, t_vec, f_vec, tf_vec = (base.clone() for _ in range(4))
        for ci in top_classes:
            direct = (audio @ frozen_evidence[frozen_indices[ci]['direct']].T).reshape(-1)
            aakv = (audio @ frozen_evidence[frozen_indices[ci]['aakv']].T).reshape(-1)
            i_vec[ci] = joint(base[ci], direct)
            t_vec[ci] = joint(base[ci], aakv)
            f_vec[ci] = hierarchical(base[ci], direct)
            tf_vec[ci] = hierarchical(base[ci], aakv)
        vectors.update({'I_Frozen-iKnow-05b': i_vec, 'T_AAKV-only': t_vec,
                        'F_Fusion-only': f_vec, 'TF_AAKV+Fusion': tf_vec})

        spaces = {'S': {}, 'TS': {}, 'FS': {}, 'TFS': {}}
        for relation in relations:
            dj, aj, dh, ah = (base.clone() for _ in range(4))
            for ci in top_classes:
                raw_ids = relation_keys[relation].get(ci, [])
                ids = [key_to_index[k] for k in raw_ids]
                prompt_ids = [prompt_to_index[prompt] for _, prompt in relation_cache['tails'][relation].get(ci, [])]
                direct = (audio @ all_prompt_embeddings[prompt_ids].T).reshape(-1) if prompt_ids else torch.empty(0, device=device)
                aakv = aakv_similarity[ids] if ids else torch.empty(0, device=device)
                dj[ci] = joint(base[ci], direct); aj[ci] = joint(base[ci], aakv)
                dh[ci] = hierarchical(base[ci], direct); ah[ci] = hierarchical(base[ci], aakv)
            spaces['S'][relation] = dj; spaces['TS'][relation] = aj
            spaces['FS'][relation] = dh; spaces['TFS'][relation] = ah
        selected = {}
        for branch, method in [('S','S_Selector-only'), ('TS','TS_AAKV+Selector'),
                               ('FS','FS_Fusion+Selector'), ('TFS','TFS_AAKV+Fusion+Selector')]:
            relation, consensus, votes = select_relation(spaces[branch], relations)
            vectors[method] = spaces[branch][relation]; selected[branch] = {'relation': relation, 'consensus_class': consensus, 'votes': votes}
            selected_counts[branch][relation] += 1

        row_ranks = {m: best_positive_rank(vectors[m], sample['true_indices']) for m in METHODS}
        for method in METHODS: ranks[method].append(row_ranks[method])
        rows.append({'sample_index': index, 'audio_path': sample['audio_path'],
                     'true_indices': [int(x) for x in sample['true_indices']], 'seed': sample_seed,
                     'selected': selected, 'ranks': row_ranks})
        score_rows.append(torch.stack([vectors[m] for m in METHODS]).cpu().numpy())

    result = {m: metrics(ranks[m]) for m in METHODS}
    baseline = result['I_Frozen-iKnow-05b']
    deltas = {m: {k: result[m][k] - baseline[k] for k in baseline} for m in METHODS if m not in ('CLAP','I_Frozen-iKnow-05b')}
    np.savez_compressed(out / 'predictions.npz', scores=np.asarray(score_rows), methods=METHODS)
    save_json(out / 'samples.json', rows); save_json(out / 'metrics.json', result); save_json(out / 'delta_vs_iKnow.json', deltas)
    save_json(out / 'protocol.json', {'task': 21, 'TopP': 'All (disabled)', 'hop': 1, 'K': 5, 'M': 3,
        'R': 1, 'alpha': 0.5, 'kappa': 100, 'seed': 42, 'selector': 'Consensus-Margin-Top1',
        'selector_is_aligned_to_each_branch': True, 'labels_used_by_method': False,
        'selected_relation_counts': {b: dict(c) for b,c in selected_counts.items()}})
    header = 'method,Hit@1,Hit@3,Hit@5,MRR,delta_Hit@1_vs_iKnow,delta_MRR_vs_iKnow\n'
    lines = []
    for m in METHODS:
        dh = result[m]['Hit@1'] - baseline['Hit@1']; dm = result[m]['MRR'] - baseline['MRR']
        lines.append(f"{m},{result[m]['Hit@1']:.8f},{result[m]['Hit@3']:.8f},{result[m]['Hit@5']:.8f},{result[m]['MRR']:.8f},{dh:.8f},{dm:.8f}")
    (out / 'metrics.csv').write_text(header + '\n'.join(lines) + '\n', encoding='utf-8')
    save_json(out / 'progress.json', {'completed': True, 'n': len(samples)})

if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('dataset'); args = parser.parse_args(); main(args.dataset)
