#!/usr/bin/env python3
"""Wait for AAKV shards, merge them, then launch Task19 dataset queues."""
import json, os, subprocess, time
from pathlib import Path
ROOT=Path('/data/zkx/zkx/review1');OUT=ROOT/'19_three_factor_full_ablation'
while True:
 states=[]
 for i in range(3):
  p=OUT/f'aakv_shard_{i}.json';states.append(json.load(open(p)).get('completed',False) if p.exists() else False)
 if all(states):break
 time.sleep(30)
m=json.load(open(OUT/'aakv_manifest.json'));texts=dict(m['existing']);audit={}
for i in range(3):
 s=json.load(open(OUT/f'aakv_shard_{i}.json'))
 audit[str(i)]=s.get('audit',{})
 for x in s['rows']:texts['\t'.join((x['head'],x['relation'],x['tail']))]=x['qwen_verified']
assert len(texts)==m['needed_unique'],(len(texts),m['needed_unique'])
(OUT/'aakv_all.json').write_text(json.dumps({'texts':texts,'audit':audit},ensure_ascii=False),encoding='utf-8')
queues={0:['01_ESC50','05_AudioSet'],1:['02_UrbanSound8K','04_DCASE17_T4'],2:['03_FSD50K','06_TUT2017']}
for gpu,dss in queues.items():
 cmd=' && '.join(f'CUDA_VISIBLE_DEVICES={gpu} python {ROOT}/task19_run.py {d} > {OUT}/{d}.log 2>&1' for d in dss)
 subprocess.Popen(['bash','-lc',cmd],start_new_session=True)
(OUT/'evaluation_launched.json').write_text(json.dumps({'queues':queues,'time':time.strftime('%F %T')},indent=2))
