#!/usr/bin/env python3
"""Prepare every unique one-hop relation triple needed by aligned AAKV selector."""
import json
from pathlib import Path
import torch
ROOT=Path('/data/zkx/zkx/review1');OUT=ROOT/'20_aakv_aligned_selector';OUT.mkdir(exist_ok=True)
DS=['01_ESC50','02_UrbanSound8K','03_FSD50K','04_DCASE17_T4','05_AudioSet','06_TUT2017']
need={}
for ds in DS:
 c=torch.load(ROOT/f'18a_relation_oracle_audit/{ds}/results/static_relation_cache.pt',map_location='cpu')
 for rel in c['relations']:
  for ci,items in c['tails'][rel].items():
   for tail,prompt in items:
    head=prompt.split(', ',1)[0];need['\t'.join((head,rel,tail))]={'head':head,'relation':rel,'tail':tail}
existing={}
p=ROOT/'19_three_factor_full_ablation/aakv_all.json'
if p.exists():existing.update(json.load(open(p))['texts'])
for ds in DS:
 q=json.load(open(ROOT/f'10_hard-prefix-pilot/{ds}/prompts/qwen_generation_audit.json'))
 for x in q['rows']:existing['\t'.join((str(x['head']),str(x['relation']),str(x['tail'])))]=x['qwen_verified']
payload={'needed_unique':len(need),'reused_existing':sum(k in existing for k in need),'missing_unique':sum(k not in existing for k in need),
         'existing':{k:existing[k] for k in need if k in existing},'missing':[v for k,v in sorted(need.items()) if k not in existing]}
(OUT/'aakv_manifest.json').write_text(json.dumps(payload,ensure_ascii=False),encoding='utf-8');print({k:payload[k] for k in ['needed_unique','reused_existing','missing_unique']})
