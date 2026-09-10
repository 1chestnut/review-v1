#!/usr/bin/env python3
"""Deterministically generate one shard of missing Task19 AAKV evidence."""
import argparse, importlib.util, json, os
from pathlib import Path
from collections import Counter
import torch
from tqdm import tqdm
from transformers import AutoModelForCausalLM, AutoTokenizer

ROOT=Path('/data/zkx/zkx/review1'); OUT=ROOT/'19_three_factor_full_ablation'
MODEL=Path('/data/zkx/zkx/iknow-audio/data/model/千问')
spec=importlib.util.spec_from_file_location('qsrc',ROOT/'10_hard-prefix-pilot/code/run_qwen_verified.py')
qsrc=importlib.util.module_from_spec(spec);spec.loader.exec_module(qsrc)

def atomic(path,obj):
    tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(obj,ensure_ascii=False),encoding='utf-8');os.replace(tmp,path)

def main():
    p=argparse.ArgumentParser();p.add_argument('--shard',type=int,required=True);p.add_argument('--num-shards',type=int,default=3);a=p.parse_args()
    manifest=json.load(open(OUT/'aakv_manifest.json'));items=[x for i,x in enumerate(manifest['missing']) if i%a.num_shards==a.shard]
    path=OUT/f'aakv_shard_{a.shard}.json';state=json.load(open(path)) if path.exists() else {'completed':False,'next':0,'rows':[]}
    tok=AutoTokenizer.from_pretrained(MODEL,local_files_only=True)
    model=AutoModelForCausalLM.from_pretrained(MODEL,torch_dtype=torch.bfloat16,device_map='cuda:0',local_files_only=True);model.eval()
    rows=state['rows']
    for i in tqdm(range(state['next'],len(items)),initial=state['next'],total=len(items),desc=f'AAKV shard {a.shard}',mininterval=10):
        x=items[i];head,rel,tail=x['head'],x['relation'],x['tail']
        user=f'[head] {head}\n[relation] {rel}\n[tail] {tail}'
        system=qsrc.SYSTEM_PROMPT.replace('{head}',head);repair=qsrc.REPAIR_PROMPT.replace('{head}',head)
        msgs=[{'role':'system','content':system},{'role':'user','content':user}]
        raw=qsrc.model_generate(model,tok,msgs);clean,reasons=qsrc.validate(head,rel,tail,raw)
        outcome='accepted_first';verified=clean;repaired=None;repair_reasons=[]
        if reasons:
            repaired=qsrc.model_generate(model,tok,msgs+[{'role':'assistant','content':raw},{'role':'user','content':repair+'\nFailed checks: '+', '.join(reasons)}])
            rc,repair_reasons=qsrc.validate(head,rel,tail,repaired)
            if repair_reasons: verified=f'The sound of {head} has the relation {rel} with {tail}.';outcome='universal_fallback'
            else: verified=rc;outcome='accepted_repair'
        rows.append({**x,'qwen_verified':verified,'outcome':outcome,'first_failures':reasons,'repair_failures':repair_reasons})
        if (i+1)%25==0:atomic(path,{'completed':False,'next':i+1,'total':len(items),'rows':rows})
    atomic(path,{'completed':True,'next':len(items),'total':len(items),'rows':rows,'audit':dict(Counter(x['outcome'] for x in rows))})
if __name__=='__main__':main()
