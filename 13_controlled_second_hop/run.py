import os
os.environ['CUBLAS_WORKSPACE_CONFIG'] = ':4096:8'
os.environ['PYTHONHASHSEED'] = '42'

import argparse, csv, hashlib, importlib.util, json, math, random, time
from collections import Counter
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from pykeen.triples import TriplesFactory
from scipy.stats import binomtest
from tqdm import tqdm

ROOT = Path('/data/zkx/zkx/review1/13_controlled_second_hop')
BASE = ROOT.parent
SOURCE12 = BASE / '12_shared-abcd-statistics'
SOURCE06 = BASE / '06_onehop-text-verbalization-audit'

TOP_K = 5
TOP_M1 = 3
TOP_M2 = 1
TOP_P_TOTAL = 5
GAMMA = 0.85
METHODS = ['D-1st', 'D-2nd-Controlled']


def save(path, obj):
    path = Path(path)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding='utf-8')
    tmp.replace(path)


def seed_all(value):
    random.seed(value)
    np.random.seed(value)
    torch.manual_seed(value)
    torch.cuda.manual_seed_all(value)


def load_module(path):
    spec = importlib.util.spec_from_file_location('frozen_runtime', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def normalized_lse(values):
    return (torch.logsumexp(100.0 * values, dim=0) - math.log(values.numel())) / 100.0


def fuse(base_score, first_scores, second_scores, alpha):
    values = torch.cat([first_scores, GAMMA * second_scores])
    if not values.numel():
        return base_score, 0, []
    order = torch.argsort(values, descending=True, stable=True)[:TOP_P_TOTAL]
    selected = values[order]
    n_first = first_scores.numel()
    second_selected = int(torch.sum(order >= n_first).item())
    return alpha * base_score + (1.0 - alpha) * normalized_lse(selected), second_selected, order.cpu().tolist()


def first_only(base_score, first_scores, alpha):
    if not first_scores.numel():
        return base_score
    order = torch.argsort(first_scores, descending=True, stable=True)[:TOP_P_TOTAL]
    return alpha * base_score + (1.0 - alpha) * normalized_lse(first_scores[order])


def build_second_hop(ds, runtime, cfg, triples, out):
    cache = out / 'second_hop_knowledge.json'
    relation_list = list(cfg['relations'])
    signature = {
        'dataset': ds, 'relations': relation_list, 'top_m1': TOP_M1,
        'top_m2': TOP_M2, 'top_p_total': TOP_P_TOTAL, 'gamma': GAMMA,
        'source_triples_sha256': hashlib.sha256((out / 'frozen_inputs' / 'triples.json').read_bytes()).hexdigest(),
    }
    if cache.exists():
        payload = json.loads(cache.read_text(encoding='utf-8'))
        if payload.get('signature') == signature:
            return payload

    device = runtime.DEVICE
    model = torch.load(Path(runtime.KGE_MODEL_DIR) / 'trained_model.pkl', map_location=device)
    model.eval()
    factory = TriplesFactory.from_path(runtime.TRAIN_TRIPLES_PATH)
    runtime.TOP_M = TOP_M2
    get_tails = runtime.build_tail_predictor(model, factory)
    valid_relations = [r for r in relation_list if r in factory.relation_to_id]
    audit = Counter()
    classes = []

    for class_id, cls in enumerate(tqdm(triples['classes'], desc=f'{ds} KG audit', mininterval=5)):
        origin = str(cls.get('kg_entity') or cls.get('class_name') or '')
        origin_id = factory.entity_to_id.get(origin)
        seen_paths = set()
        seen_texts = set()
        rows = []
        for first in cls['triples']:
            middle = str(first['tail'])
            middle_id = factory.entity_to_id.get(middle)
            audit['first_hop_entities'] += 1
            if middle_id is None:
                audit['middle_not_in_entity_vocab'] += 1
                continue
            audit['middle_valid_as_second_head'] += 1
            for relation in valid_relations:
                audit['second_hop_queries'] += 1
                tails = get_tails(middle, relation)
                if not tails:
                    audit['empty_second_hop_queries'] += 1
                    continue
                tail = str(tails[0])
                tail_id = factory.entity_to_id.get(tail)
                if tail_id is None:
                    audit['predicted_tail_not_in_vocab'] += 1
                    continue
                if tail_id == middle_id:
                    audit['self_loops_removed'] += 1
                    continue
                if origin_id is not None and tail_id == origin_id:
                    audit['returns_to_origin_removed'] += 1
                    continue
                key = (middle_id, factory.relation_to_id[relation], tail_id)
                if key in seen_paths:
                    audit['duplicate_paths_removed'] += 1
                    continue
                seen_paths.add(key)
                # This is exactly Task 10's deterministic verified fallback form.
                text = f'The sound of {middle} has the relation {relation} with {tail}.'
                norm_text = ' '.join(text.lower().split())
                if norm_text in seen_texts:
                    audit['duplicate_texts_removed'] += 1
                    continue
                seen_texts.add(norm_text)
                rows.append({
                    'class_id': class_id,
                    'origin': origin, 'origin_id': origin_id,
                    'middle': middle, 'middle_id': middle_id,
                    'relation': relation, 'relation_id': factory.relation_to_id[relation],
                    'tail': tail, 'tail_id': tail_id,
                    'text': text,
                })
                audit['retained_paths'] += 1
        if not rows:
            audit['classes_without_valid_second_hop'] += 1
        classes.append(rows)

    audit['classes'] = len(classes)
    audit['valid_relations'] = len(valid_relations)
    audit['invalid_relations'] = len(relation_list) - len(valid_relations)
    payload = {'signature': signature, 'valid_relations': valid_relations,
               'audit': dict(audit), 'classes': classes}
    save(cache, payload)
    del model
    torch.cuda.empty_cache()
    return payload


def paired_statistics(ranks, out):
    ranks = np.asarray(ranks)
    hit = (ranks == 1).astype(float)
    rr = 1.0 / ranks
    delta_hit = 100.0 * (hit[:, 1] - hit[:, 0])
    delta_rr = 100.0 * (rr[:, 1] - rr[:, 0])
    rng = np.random.default_rng(42)
    boots = np.empty((10000, 2))
    for i in range(10000):
        ids = rng.integers(0, len(ranks), len(ranks))
        boots[i] = [delta_hit[ids].mean(), delta_rr[ids].mean()]
    gain = int(np.sum((hit[:, 1] == 1) & (hit[:, 0] == 0)))
    loss = int(np.sum((hit[:, 1] == 0) & (hit[:, 0] == 1)))
    result = {
        'comparison': 'D-2nd-Controlled minus D-1st',
        'n_clips': len(ranks), 'bootstrap_replicates': 10000, 'seed': 42,
        'delta_Hit@1_pp': float(delta_hit.mean()),
        'delta_Hit@1_bootstrap95': np.quantile(boots[:, 0], [.025, .975]).tolist(),
        'delta_MRR_pp': float(delta_rr.mean()),
        'delta_MRR_bootstrap95': np.quantile(boots[:, 1], [.025, .975]).tolist(),
        'wrong_to_right': gain, 'right_to_wrong': loss,
        'mcnemar_exact_two_sided_p': float(binomtest(gain, gain + loss, .5).pvalue) if gain + loss else 1.0,
        'rank_improved': int(np.sum(ranks[:, 1] < ranks[:, 0])),
        'rank_worsened': int(np.sum(ranks[:, 1] > ranks[:, 0])),
        'rank_unchanged': int(np.sum(ranks[:, 1] == ranks[:, 0])),
    }
    save(out / 'statistics.json', result)
    return result


@torch.inference_mode()
def main(ds):
    seed_all(42)
    torch.use_deterministic_algorithms(True)
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = True
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False

    out = ROOT / ds
    out.mkdir(parents=True, exist_ok=True)
    frozen = out / 'frozen_inputs'
    frozen.mkdir(exist_ok=True)

    source12 = SOURCE12 / ds
    source06 = SOURCE06 / ds
    sources = {
        'runtime.py': source12 / 'frozen_inputs/runtime.py',
        'config.json': source12 / 'frozen_inputs/config.json',
        'triples.json': source12 / 'frozen_inputs/triples.json',
        'aakv.json': source12 / 'frozen_inputs/aakv.json',
        'mapping.json': source12 / 'frozen_inputs/mapping.json',
    }
    hashes = {}
    for name, src in sources.items():
        dst = frozen / name
        if not dst.exists():
            dst.write_bytes(src.read_bytes())
        hashes[name] = hashlib.sha256(dst.read_bytes()).hexdigest()

    cfg = json.loads((frozen / 'config.json').read_text(encoding='utf-8'))
    triples = json.loads((frozen / 'triples.json').read_text(encoding='utf-8'))
    runtime = load_module(frozen / 'runtime.py')
    knowledge = build_second_hop(ds, runtime, cfg, triples, out)

    task12_text = torch.load(source12 / 'text_embeddings.pt', map_location='cuda')
    label_emb = task12_text['labels'].to('cuda')
    first_emb = task12_text['evidence'].to('cuda')
    first_index = task12_text['indices']

    unique_texts, text_to_id, second_index = [], {}, []
    for rows in knowledge['classes']:
        ids = []
        for row in rows:
            text = row['text']
            if text not in text_to_id:
                text_to_id[text] = len(unique_texts)
                unique_texts.append(text)
            ids.append(text_to_id[text])
        second_index.append(ids)

    clap = runtime.CLAP(version='2023', use_cuda=True)
    clap.clap.eval()
    chunks = []
    for start in tqdm(range(0, len(unique_texts), 128), desc=f'{ds} second-hop text'):
        chunks.append(F.normalize(runtime.get_safe_text_embeddings(
            clap, unique_texts[start:start + 128], 'cuda'), dim=-1))
    second_emb = torch.cat(chunks) if chunks else torch.empty((0, label_emb.shape[1]), device='cuda')
    torch.save({'texts': unique_texts, 'embeddings': second_emb.cpu(),
                'class_index': second_index}, out / 'second_hop_text_embeddings.pt')

    dataset = runtime.load_dataset()
    samples = list(runtime.iter_samples(dataset))
    ranks, rows, all_scores, all_orders = [], [], [], []
    usage = Counter()
    for i, sample in enumerate(tqdm(samples, desc=ds, mininterval=10)):
        audio = torch.load(source12 / 'audio_cache' / f'{i:06d}.pt', map_location='cuda')
        base_scores = (audio @ label_emb.T).squeeze(0)
        first_scores_all = (audio @ first_emb.T).squeeze(0)
        second_scores_all = (audio @ second_emb.T).squeeze(0) if second_emb.numel() else torch.empty(0, device='cuda')
        top = torch.argsort(base_scores, descending=True)[:TOP_K].tolist()
        alpha = float(np.clip(.4 + .4 * float(base_scores.max()), .4, .8))
        vectors = {m: base_scores.clone() for m in METHODS}
        class_usage = []
        for class_id in top:
            ids1 = first_index[class_id]['aakv']
            ids2 = second_index[class_id]
            s1 = first_scores_all[ids1] if ids1 else torch.empty(0, device='cuda')
            s2 = second_scores_all[ids2] if ids2 else torch.empty(0, device='cuda')
            vectors['D-1st'][class_id] = first_only(base_scores[class_id], s1, alpha)
            value, selected2, selected_order = fuse(base_scores[class_id], s1, s2, alpha)
            vectors['D-2nd-Controlled'][class_id] = value
            usage['topk_class_queries'] += 1
            usage['second_candidates_offered'] += int(s2.numel())
            usage['second_selected_top_p'] += selected2
            usage['classes_with_second_available'] += int(s2.numel() > 0)
            usage['classes_with_second_selected'] += int(selected2 > 0)
            class_usage.append({'class_id': class_id, 'h1_count': int(s1.numel()),
                                'h2_count': int(s2.numel()), 'h2_selected': selected2,
                                'joint_top_p_order': selected_order})
        orders = torch.stack([torch.argsort(vectors[m], descending=True) for m in METHODS]).cpu().numpy()
        sample_ranks = [min(int(np.where(order == y)[0][0]) + 1 for y in sample['true_indices']) for order in orders]
        ranks.append(sample_ranks)
        all_scores.append(torch.stack([vectors[m] for m in METHODS]).cpu().numpy())
        all_orders.append(orders)
        rows.append({'sample_index': i, 'audio_path': sample['audio_path'],
                     'true_indices': [int(x) for x in sample['true_indices']],
                     'topk': top, 'alpha': alpha,
                     'ranks': dict(zip(METHODS, sample_ranks)), 'class_usage': class_usage})
        usage['samples'] += 1
        usage['samples_with_any_second_selected'] += int(any(x['h2_selected'] > 0 for x in class_usage))
        if (i + 1) % 50 == 0:
            save(out / 'progress.json', {'completed': False, 'done': i + 1, 'total': len(samples)})

    rank_array = np.asarray(ranks)
    metrics = {}
    for j, method in enumerate(METHODS):
        r = rank_array[:, j]
        metrics[method] = {'Hit@1': float(100 * np.mean(r <= 1)),
                           'Hit@3': float(100 * np.mean(r <= 3)),
                           'Hit@5': float(100 * np.mean(r <= 5)),
                           'MRR': float(100 * np.mean(1.0 / r))}
    save(out / 'metrics.json', metrics)
    with (out / 'metrics.csv').open('w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['method', 'Hit@1', 'Hit@3', 'Hit@5', 'MRR'])
        for method in METHODS:
            writer.writerow([method] + [metrics[method][x] for x in ['Hit@1', 'Hit@3', 'Hit@5', 'MRR']])
    save(out / 'samples.json', rows)
    np.savez_compressed(out / 'predictions.npz', scores=np.asarray(all_scores),
                        orders=np.asarray(all_orders), ranks=rank_array, methods=METHODS)
    statistics = paired_statistics(ranks, out)
    save(out / 'protocol.json', {
        'purpose': 'exploratory test of controlled second-hop incremental value',
        'frozen_task12_baseline': 'D = AAKV + dynamic alpha + total Top-P=5',
        'only_method_change': 'add valid second-hop candidates to the same total Top-P pool',
        'top_k': TOP_K, 'top_m1': TOP_M1, 'top_m2': TOP_M2,
        'top_p_total': TOP_P_TOTAL, 'gamma': GAMMA,
        'gate': False, 'same_relations_both_hops': True,
        'filters': ['entity-ID validity', 'self-loop', 'return-to-origin', 'exact path duplicate', 'exact text duplicate'],
        'second_hop_verbalizer': 'Task10 deterministic verified universal fallback; no manual relation template',
        'audio_cache': str(source12 / 'audio_cache'), 'source_hashes': hashes,
        'important_limitation': 'Exploratory fixed M2/gamma values, not a final validation-selected protocol.',
    })
    save(out / 'usage_audit.json', dict(usage))
    save(out / 'progress.json', {'completed': True, 'done': len(samples), 'total': len(samples)})
    print(json.dumps({'metrics': metrics, 'statistics': statistics,
                      'knowledge_audit': knowledge['audit'], 'usage': dict(usage)}, indent=2), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('dataset')
    args = parser.parse_args()
    main(args.dataset)
