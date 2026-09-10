#!/usr/bin/env python3
"""Generate one deterministic shard of missing Task20 AAKV texts."""
import argparse,importlib.util,json,os
from pathlib import Path
from collections import Counter
import torch
from tqdm import tqdm
from transformers import AutoModelForCausalLM,AutoTokenizer
ROOT=Path('/data/zkx/zkx/review1');OUT=ROOT/'20_aakv_aligned_selector';MODEL=Path('/data/zkx/zkx/iknow-audio/data/model/千问')
s=importlib.util.spec_from_file_location('qsrc',ROOT/'10_hard-prefix-pilot/code/run_qwen_verified.py');q=importlib.util.module_from_spec(s);s.loader.exec_module(q)
def save(p,x):
 t=p.with_suffix('.tmp');t.write_text(json.dumps(x,ensure_ascii=False),encoding='utf-8');os.replace(t,p)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--shard',type=int,required=True);ap.add_argument('--num-shards',type=int,default=3);a=ap.parse_args()
 m=json.load(open(OUT/'aakv_manifest.json'));items=[x for i,x in enumerate(m['missing']) if i%a.num_shards==a.shard];path=OUT/f'shard_{a.shard}.json'
 st=json.load(open(path)) if path.exists() else {'next':0,'rows':[]};rows=st['rows']
 tok=AutoTokenizer.from_pretrained(MODEL,local_files_only=True);model=AutoModelForCausalLM.from_pretrained(MODEL,torch_dtype=torch.bfloat16,device_map='cuda:0',local_files_only=True);model.eval()
 for i in tqdm(range(st['next'],len(items)),initial=st['next'],total=len(items),desc=f'T20 shard {a.shard}',mininterval=10):
  x=items[i];h,r,t=x['head'],x['relation'],x['tail'];user=f'[head] {h}\n[relation] {r}\n[tail] {t}';sys=q.SYSTEM_PROMPT.replace('{head}',h);repair=q.REPAIR_PROMPT.replace('{head}',h);msgs=[{'role':'system','content':sys},{'role':'user','content':user}]
  raw=q.model_generate(model,tok,msgs);clean,reasons=q.validate(h,r,t,raw);verified=clean;outcome='accepted_first';rep=[]
  if reasons:
   rr=q.model_generate(model,tok,msgs+[{'role':'assistant','content':raw},{'role':'user','content':repair+'\nFailed checks: '+', '.join(reasons)}]);rc,rep=q.validate(h,r,t,rr)
   if rep:verified=f'The sound of {h} has the relation {r} with {t}.';outcome='universal_fallback'
   else:verified=rc;outcome='accepted_repair'
  rows.append({**x,'qwen_verified':verified,'outcome':outcome,'first_failures':reasons,'repair_failures':rep})
  if (i+1)%25==0:save(path,{'completed':False,'next':i+1,'total':len(items),'rows':rows})
 save(path,{'completed':True,'next':len(items),'total':len(items),'rows':rows,'audit':dict(Counter(x['outcome'] for x in rows))})
if __name__=='__main__':main()
