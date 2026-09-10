#!/usr/bin/env python3
"""Build the exact AAKV triples required by frozen Task18C Top-1 selections."""
import json
from pathlib import Path
import torch

ROOT=Path('/data/zkx/zkx/review1')
OUT=ROOT/'19_three_factor_full_ablation'; OUT.mkdir(exist_ok=True)
DATASETS=['01_ESC50','02_UrbanSound8K','03_FSD50K','04_DCASE17_T4','05_AudioSet','06_TUT2017']
need={}
existing={}
for ds in DATASETS:
    cache=torch.load(ROOT/f'18a_relation_oracle_audit/{ds}/results/static_relation_cache.pt',map_location='cpu')
    r18=json.load(open(ROOT/f'18c_discriminative_relation_selector/{ds}/results/discriminative_selector_results.json'))
    s12=json.load(open(ROOT/f'12_shared-abcd-statistics/{ds}/samples.json'))
    top={x['audio_path']:x['topk'] for x in s12}
    for row in r18['rows']:
        rel=row['selected_relations']['Consensus-Margin-Top1'][0]
        for ci in top[row['audio_path']]:
            for tail,prompt in cache['tails'][rel].get(ci,[]):
                head=prompt.split(', ',1)[0]
                key='\t'.join((head,rel,tail))
                need[key]={'head':head,'relation':rel,'tail':tail}
    q=json.load(open(ROOT/f'10_hard-prefix-pilot/{ds}/prompts/qwen_generation_audit.json'))
    for x in q['rows']:
        key='\t'.join((str(x['head']),str(x['relation']),str(x['tail'])))
        existing[key]=x['qwen_verified']
missing=[v for k,v in sorted(need.items()) if k not in existing]
payload={'datasets':DATASETS,'needed_unique':len(need),'reused_existing':sum(k in existing for k in need),
         'missing_unique':len(missing),'existing':{k:existing[k] for k in need if k in existing},'missing':missing}
(OUT/'aakv_manifest.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
print({k:payload[k] for k in ['needed_unique','reused_existing','missing_unique']})
