#!/usr/bin/env python3
"""Compare frozen relations, old Direct selector, and AAKV-aligned selector."""
import os
os.environ['CUBLAS_WORKSPACE_CONFIG']=':4096:8';os.environ['PYTHONHASHSEED']='42'
import argparse,hashlib,importlib.util,json,math,random
from collections import Counter
from pathlib import Path
import numpy as np
import torch
import torch.nn.functional as F
from tqdm import tqdm
ROOT=Path('/data/zkx/zkx/review1');TASK=ROOT/'20_aakv_aligned_selector'
METHODS=['CLAP','E_AAKV+Fusion-FrozenRelations','H-old_DirectSelected-AAKVScored','H-aligned_AAKVSelected-AAKVScored']
def seed(v):
 random.seed(v);np.random.seed(v%(2**32-1));torch.manual_seed(v);torch.cuda.manual_seed_all(v)
def mod(p):
 s=importlib.util.spec_from_file_location('rt20',str(p));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def nlse(v,k):return (torch.logsumexp(k*v,0)-math.log(v.numel()))/k
def hier(b,e):
 if not e.numel():return b
 e=e[torch.argsort(e,descending=True,stable=True)[:5]];return .5*b+.5*nlse(e,100.)
def rank(z,t):
 o=torch.argsort(z,descending=True).cpu().numpy();return min(int(np.where(o==int(y))[0][0])+1 for y in t)
def metric(r):
 x=np.asarray(r,float);return {'Hit@1':float(100*np.mean(x<=1)),'Hit@3':float(100*np.mean(x<=3)),'Hit@5':float(100*np.mean(x<=5)),'MRR':float(100*np.mean(1/x))}
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
def main(ds):
 out=TASK/ds;out.mkdir(exist_ok=True);src=ROOT/'12_shared-abcd-statistics'/ds;snap=src/'frozen_inputs';rt=mod(snap/'runtime.py');dev=rt.DEVICE
 seed(42);torch.use_deterministic_algorithms(True);torch.backends.cudnn.benchmark=False;torch.backends.cudnn.deterministic=True;torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
 clap=rt.CLAP(version='2023',use_cuda=True);clap.clap.eval();data=rt.load_dataset();samples=list(rt.iter_samples(data));frozen=torch.load(src/'text_embeddings.pt',map_location='cpu');le=frozen['labels'].to(dev);fe=frozen['evidence'].to(dev);fidx=frozen['indices']
 cache=torch.load(ROOT/f'18a_relation_oracle_audit/{ds}/results/static_relation_cache.pt',map_location='cpu');rels=cache['relations'];texts=json.load(open(TASK/'aakv_all.json'))['texts']
 keys=[];seen=set();rid={r:{} for r in rels}
 for r in rels:
  for ci,items in cache['tails'][r].items():
   ids=[]
   for tail,prompt in items:
    k='\t'.join((prompt.split(', ',1)[0],r,tail))
    if k not in seen:seen.add(k);keys.append(k)
    ids.append(k)
   rid[r][int(ci)]=ids
 atexts=[texts[k] for k in keys];keyid={k:i for i,k in enumerate(keys)};chunks=[]
 for i in range(0,len(atexts),128):chunks.append(F.normalize(rt.get_safe_text_embeddings(clap,atexts[i:i+128],dev),dim=-1))
 ae=torch.cat(chunks);old=json.load(open(ROOT/f'18c_discriminative_relation_selector/{ds}/results/discriminative_selector_results.json'));oldsel={x['audio_path']:x['selected_relations']['Consensus-Margin-Top1'][0] for x in old['rows']}
 ranks={m:[] for m in METHODS};rows=[];scores_all=[];counts=Counter()
 for i,s in enumerate(tqdm(samples,desc=ds,mininterval=10)):
  sd=int(hashlib.sha256(('42|'+s['audio_path']).encode()).hexdigest()[:8],16);seed(sd);ac=src/'audio_cache'/f'{i:06d}.pt';audio=torch.load(ac,map_location=dev);base=(audio@le.T).squeeze(0);top=torch.argsort(base,descending=True)[:5].tolist();evall=(audio@ae.T).squeeze(0)
  E=base.clone()
  for ci in top:E[ci]=hier(base[ci],(audio@fe[fidx[ci]['aakv']].T).reshape(-1))
  single={};margin={};pred={}
  for r in rels:
   z=base.clone()
   for ci in top:
    ids=[keyid[k] for k in rid[r].get(ci,[])];z[ci]=hier(base[ci],evall[ids] if ids else torch.empty(0,device=dev))
   single[r]=z;v=torch.topk(z,k=min(2,z.numel())).values;margin[r]=float(v[0]-v[1]) if v.numel()>1 else 0.;pred[r]=int(torch.argmax(z))
  votes=Counter(pred.values());mv=max(votes.values());cands=sorted(c for c,n in votes.items() if n==mv);cc=max(cands,key=lambda c:(sum(margin[r] for r in rels if pred[r]==c),-c));support=sorted((r for r in rels if pred[r]==cc),key=lambda r:(-margin[r],r));aligned=support[0];counts[aligned]+=1
  oldr=oldsel[s['audio_path']];Hold=single[oldr];Ha=single[aligned];vec={'CLAP':base,'E_AAKV+Fusion-FrozenRelations':E,'H-old_DirectSelected-AAKVScored':Hold,'H-aligned_AAKVSelected-AAKVScored':Ha};rr={m:rank(vec[m],s['true_indices']) for m in METHODS}
  for m in METHODS:ranks[m].append(rr[m])
  rows.append({'sample_index':i,'audio_path':s['audio_path'],'true_indices':[int(x) for x in s['true_indices']],'seed':sd,'old_relation':oldr,'aligned_relation':aligned,'consensus_class':cc,'consensus_votes':mv,'ranks':rr});scores_all.append(torch.stack([vec[m] for m in METHODS]).cpu().numpy())
 met={m:metric(ranks[m]) for m in METHODS};np.savez_compressed(out/'predictions.npz',scores=np.asarray(scores_all),methods=METHODS);save(out/'samples.json',rows);save(out/'metrics.json',met);save(out/'protocol.json',{'only_changed_variable':'relation selection scoring space','K':5,'M':3,'P':5,'R':1,'alpha':.5,'kappa':100,'hop':1,'selector':'Consensus-Margin-Top1','labels_used':False,'selection_counts':dict(counts)})
 (out/'metrics.csv').write_text('method,Hit@1,Hit@3,Hit@5,MRR\n'+'\n'.join(f"{m},{met[m]['Hit@1']:.8f},{met[m]['Hit@3']:.8f},{met[m]['Hit@5']:.8f},{met[m]['MRR']:.8f}" for m in METHODS)+'\n');save(out/'progress.json',{'completed':True,'n':len(samples)})
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('dataset');a=p.parse_args();main(a.dataset)
