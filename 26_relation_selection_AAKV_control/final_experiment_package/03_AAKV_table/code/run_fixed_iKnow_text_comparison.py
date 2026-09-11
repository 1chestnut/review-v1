#!/usr/bin/env python3
"""Task 11: text-only ablation under the frozen reproduced iKnow aggregator."""

import argparse
import importlib.util
import json
import math
import os
import time
import warnings
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from tqdm import tqdm

ROOT = Path('/data/zkx/zkx/review1')
SOURCE_ROOT = ROOT / '06_onehop-text-verbalization-audit'
AAKV_ROOT = ROOT / '10_hard-prefix-pilot'
GENERAL_ROOT = ROOT / '09_qwen-verified-verbalization'
TASK_ROOT = ROOT / '11_iknow-formula-text-contribution'
TOP_K = 5


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def metrics(ranks):
    v = np.asarray(ranks, dtype=np.float64)
    return {'Hit@1': float(100*np.mean(v <= 1)), 'Hit@3': float(100*np.mean(v <= 3)),
            'Hit@5': float(100*np.mean(v <= 5)), 'MRR': float(100*np.mean(1.0/v))}


def rank_of_true(scores, true_indices):
    order = torch.argsort(scores, descending=True).detach().cpu().tolist()
    return min(order.index(int(target)) + 1 for target in true_indices)


def normalized_lse(values, scale):
    return (torch.logsumexp(scale*values, dim=0) - math.log(values.numel())) / scale


def iknow_joint_lse(base_score, evidence_scores, scale):
    if evidence_scores.numel() == 0:
        return base_score
    return normalized_lse(torch.cat([base_score.reshape(1), evidence_scores]), scale)


@torch.no_grad()
def main(dataset_dir):
    source = SOURCE_ROOT / dataset_dir
    aakv_file = AAKV_ROOT / dataset_dir / 'prompts/qwen_generation_audit.json'
    general_file = GENERAL_ROOT / dataset_dir / 'prompts/qwen_generation_audit.json'
    if not aakv_file.exists():
        raise FileNotFoundError(f'AAKV generation is not complete: {aakv_file}')
    if not general_file.exists():
        raise FileNotFoundError(f'General Qwen generation is not complete: {general_file}')
    out = TASK_ROOT / dataset_dir
    result_dir = out / 'results'; cache_dir = out / 'cache'
    result_dir.mkdir(parents=True, exist_ok=True); cache_dir.mkdir(parents=True, exist_ok=True)

    source_script = load_module(source/'run_onehop_text_audit.py', f'task06_{dataset_dir}')
    base = source_script.load_runtime(); config = source_script.CONFIG; device = base.DEVICE
    clap = base.CLAP(version='2023', use_cuda=torch.cuda.is_available())
    # Loaded only because Task 06 runtime initialization expects the same frozen resources.
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        kge = torch.load(os.path.join(base.KGE_MODEL_DIR, 'trained_model.pkl'), map_location=device)
    kge.eval()
    dataset = base.load_dataset(); samples = list(base.iter_samples(dataset))
    labels = list(dataset['label_classes'])
    label_emb = F.normalize(base.get_safe_text_embeddings(clap, labels, device), dim=-1)

    source_json = json.loads((source/'cache/triples_and_texts.json').read_text(encoding='utf-8'))
    aakv = json.loads(aakv_file.read_text(encoding='utf-8'))
    general = json.loads(general_file.read_text(encoding='utf-8'))
    aakv_by_key = {(r['class_id'],r['triple_id']):r for r in aakv['rows']}
    general_by_key = {(r['class_id'],r['triple_id']):r for r in general['rows']}
    forms = ['iKnow-05-Direct','RawTriple','Qwen-General','AAKV']
    all_texts=[]; class_index=[]
    for class_id, cls in enumerate(source_json['classes']):
        ids={f:[] for f in forms}
        for triple_id,row in enumerate(cls['triples']):
            texts = {
                'iKnow-05-Direct': row['direct'],
                'RawTriple': row['raw'],
                'Qwen-General': general_by_key[(class_id,triple_id)]['qwen_constrained'],
                'AAKV': aakv_by_key[(class_id,triple_id)]['qwen_verified'],
            }
            for form in forms:
                ids[form].append(len(all_texts)); all_texts.append(texts[form])
        class_index.append(ids)

    chunks=[]
    for start in range(0,len(all_texts),128):
        chunks.append(F.normalize(base.get_safe_text_embeddings(clap,all_texts[start:start+128],device),dim=-1))
    evidence_emb=torch.cat(chunks) if chunks else torch.empty((0,label_emb.shape[1]),device=device)
    torch.save({'texts':all_texts,'class_index':class_index,'forms':forms,
                'source_task06':str(source),'general_qwen_source':str(general_file),
                'aakv_source':str(aakv_file)},cache_dir/'text_embeddings.pt')

    methods=['CLAP']+forms
    ranks={m:[] for m in methods}; rows=[]; scale=float(config['logit_scale'])
    for sample_index,sample in enumerate(tqdm(samples,desc=f'Task11 {dataset_dir}',mininterval=10)):
        if not os.path.exists(sample['audio_path']) or not sample['true_indices']:
            continue
        try:
            audio=F.normalize(base.to_tensor(clap.get_audio_embeddings([sample['audio_path']])).to(device).float(),dim=-1)
        except Exception:
            continue
        base_scores=torch.matmul(audio,label_emb.T).squeeze(0)
        evidence_scores=torch.matmul(audio,evidence_emb.T).squeeze(0)
        top_indices=torch.argsort(base_scores,descending=True)[:TOP_K].tolist()
        vectors={m:base_scores.clone() for m in methods}
        for class_id in top_indices:
            for form in forms:
                ids=class_index[class_id][form]
                scores=evidence_scores[ids] if ids else torch.empty(0,device=device)
                vectors[form][class_id]=iknow_joint_lse(base_scores[class_id],scores,scale)
        sr={m:rank_of_true(v,sample['true_indices']) for m,v in vectors.items()}
        for m in methods: ranks[m].append(int(sr[m]))
        rows.append({'sample_index':sample_index,'audio_path':sample['audio_path'],
                     'true_indices':[int(x) for x in sample['true_indices']],
                     'topk':top_indices,'ranks':sr})
        if len(rows)%20==0:
            (result_dir/'progress.json').write_text(json.dumps({'completed':False,'samples':rows},ensure_ascii=False),encoding='utf-8')

    table={m:metrics(ranks[m]) for m in methods}
    payload={'completed':True,'dataset':config['dataset'],
             'protocol':{'research_variable':'text_only','aggregator':'frozen reproduced iKnow joint normalized LSE',
                         'formula':'(logsumexp(kappa*[s_base,evidence])-log(1+n))/kappa',
                         'logit_scale_kappa':scale,'top_k':TOP_K,'top_m':3,'hop':1,
                         'relations':config['relations'],'uses_dynamic_alpha':False,'uses_ours_fusion':False,
                         'uses_second_hop':False,'source_task06':str(source)},
             'general_generation_audit':general.get('audit',{}),
             'aakv_generation_audit':aakv.get('audit',{}),'metrics':table,'samples':rows,
             'created_at':time.strftime('%Y-%m-%d %H:%M:%S')}
    (result_dir/'iknow_formula_text_ablation.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
    lines=['method,Hit@1,Hit@3,Hit@5,MRR']
    for m in methods:
        x=table[m]; lines.append(f"{m},{x['Hit@1']:.8f},{x['Hit@3']:.8f},{x['Hit@5']:.8f},{x['MRR']:.8f}")
    (result_dir/'iknow_formula_text_ablation.csv').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    (result_dir/'progress.json').write_text(json.dumps({'completed':True,'samples':rows},ensure_ascii=False),encoding='utf-8')
    print(json.dumps(table,indent=2),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('dataset_dir'); args=p.parse_args(); main(args.dataset_dir)
