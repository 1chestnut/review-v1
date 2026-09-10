#!/usr/bin/env python3
import json,subprocess,time
from pathlib import Path
ROOT=Path('/data/zkx/zkx/review1');OUT=ROOT/'20_aakv_aligned_selector'
while True:
 if all((OUT/f'shard_{i}.json').exists() and json.load(open(OUT/f'shard_{i}.json')).get('completed') for i in range(3)):break
 time.sleep(30)
m=json.load(open(OUT/'aakv_manifest.json'));texts=dict(m['existing']);audit={}
for i in range(3):
 s=json.load(open(OUT/f'shard_{i}.json'));audit[str(i)]=s.get('audit',{})
 for x in s['rows']:texts['\t'.join((x['head'],x['relation'],x['tail']))]=x['qwen_verified']
assert len(texts)==m['needed_unique'];(OUT/'aakv_all.json').write_text(json.dumps({'texts':texts,'audit':audit},ensure_ascii=False),encoding='utf-8')
Q={0:['01_ESC50','05_AudioSet'],1:['02_UrbanSound8K','04_DCASE17_T4'],2:['03_FSD50K','06_TUT2017']}
for g,ds in Q.items():
 cmd=' && '.join(f'CUDA_VISIBLE_DEVICES={g} python {ROOT}/task20_run.py {d} > {OUT}/{d}.log 2>&1' for d in ds);subprocess.Popen(['bash','-lc',cmd],start_new_session=True)
(OUT/'launched.json').write_text(json.dumps({'queues':Q,'time':time.strftime('%F %T')},indent=2))
