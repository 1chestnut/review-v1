#!/usr/bin/env python3
"""Task19 independent 2^3 factorial ablation; one hop only."""
import argparse, hashlib, importlib.util, json, math, os, random, time
os.environ['CUBLAS_WORKSPACE_CONFIG']=':4096:8'
os.environ['PYTHONHASHSEED']='42'
from pathlib import Path
from collections import Counter
import numpy as np
import torch
import torch.nn.functional as F
from tqdm import tqdm

ROOT=Path('/data/zkx/zkx/review1'); TASK=ROOT/'19_three_factor_full_ablation'
METHODS=['CLAP','Frozen-iKnow-05b','A_iKnow-TopP5-Control','B_Text-only','C_Fusion-only','D_Selector-only','E_Text+Fusion','F_Text+Selector','G_Fusion+Selector','H_Full']

def seed(v):
 random.seed(v);np.random.seed(v%(2**32-1));torch.manual_seed(v)
 if torch.cuda.is_available():torch.cuda.manual_seed_all(v)
def atom(p,x):
 p=Path(p);t=p.with_suffix(p.suffix+'.tmp');t.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8');os.replace(t,p)
def module(p):
 s=importlib.util.spec_from_file_location('rt19',str(p));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def nlse(v,k): return (torch.logsumexp(k*v,0)-math.log(v.numel()))/k
def joint(b,e,k,p=None):
 if not e.numel():return b
 if p is not None:e=e[torch.argsort(e,descending=True,stable=True)[:p]]
 return nlse(torch.cat([b.reshape(1),e]),k)
def hier(b,e,k,p=5):
 if not e.numel():return b
 e=e[torch.argsort(e,descending=True,stable=True)[:p]]
 return .5*b+.5*nlse(e,k)
def rank(z,truth):
 o=torch.argsort(z,descending=True).cpu().numpy();return min(int(np.where(o==int(y))[0][0])+1 for y in truth)
def metrics(rs):
 x=np.asarray(rs,float);return {'Hit@1':float(100*np.mean(x<=1)),'Hit@3':float(100*np.mean(x<=3)),'Hit@5':float(100*np.mean(x<=5)),'MRR':float(100*np.mean(1/x))}

def main(ds):
 out=TASK/ds;out.mkdir(parents=True,exist_ok=True)
 src=ROOT/'12_shared-abcd-statistics'/ds; snap=src/'frozen_inputs';cfg=json.load(open(snap/'config.json'))
 rt=module(snap/'runtime.py');dev=rt.DEVICE
 seed(42);torch.use_deterministic_algorithms(True);torch.backends.cudnn.benchmark=False;torch.backends.cudnn.deterministic=True;torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
 clap=rt.CLAP(version='2023',use_cuda=True);clap.clap.eval();data=rt.load_dataset();samples=list(rt.iter_samples(data));labels=list(data['label_classes'])
 frozen=torch.load(src/'text_embeddings.pt',map_location='cpu');label_emb=frozen['labels'].to(dev);frozen_emb=frozen['evidence'].to(dev);fidx=frozen['indices']
 rcache=torch.load(ROOT/f'18a_relation_oracle_audit/{ds}/results/static_relation_cache.pt',map_location='cpu');direct_emb=rcache['prompt_embeddings'].to(dev);pidx={p:i for i,p in enumerate(rcache['prompts'])}
 select=json.load(open(ROOT/f'18c_discriminative_relation_selector/{ds}/results/discriminative_selector_results.json'))
 selected={x['audio_path']:x['selected_relations']['Consensus-Margin-Top1'][0] for x in select['rows']}
 manifest=json.load(open(TASK/'aakv_all.json'));amap=manifest['texts']
 needed=[];seen=set()
 for rel in set(selected.values()):
  for ci,items in rcache['tails'][rel].items():
   for tail,prompt in items:
    head=prompt.split(', ',1)[0];key='\t'.join((head,rel,tail))
    if key in amap and key not in seen:seen.add(key);needed.append(key)
 atexts=[amap[k] for k in needed];akey={k:i for i,k in enumerate(needed)}
 chunks=[]
 for i in range(0,len(atexts),128):chunks.append(F.normalize(rt.get_safe_text_embeddings(clap,atexts[i:i+128],dev),dim=-1))
 aemb=torch.cat(chunks) if chunks else torch.empty((0,label_emb.shape[1]),device=dev)
 ranks={m:[] for m in METHODS};rows=[];all_scores=[];K=5;P=5;kappa=100.0
 for i,s in enumerate(tqdm(samples,desc=ds,mininterval=10)):
  ap=s['audio_path'];sample_seed=int(hashlib.sha256(('42|'+ap).encode()).hexdigest()[:8],16);seed(sample_seed)
  acache=src/'audio_cache'/f'{i:06d}.pt';audio=torch.load(acache,map_location=dev) if acache.exists() else F.normalize(rt.to_tensor(clap.get_audio_embeddings([ap])).to(dev).float(),dim=-1)
  base=(audio@label_emb.T).squeeze(0);top=torch.argsort(base,descending=True)[:K].tolist();rel=selected[ap]
  vectors={m:base.clone() for m in METHODS}
  for ci in top:
   fd=frozen_emb[fidx[ci]['direct']];fa=frozen_emb[fidx[ci]['aakv']]
   ed=(audio@fd.T).reshape(-1);ea=(audio@fa.T).reshape(-1)
   sd=[];sa=[]
   for tail,prompt in rcache['tails'][rel].get(ci,[]):
    sd.append((audio@direct_emb[pidx[prompt]].reshape(-1,1)).reshape(()))
    head=prompt.split(', ',1)[0];key='\t'.join((head,rel,tail))
    if key not in akey:raise RuntimeError('Missing AAKV '+key)
    sa.append((audio@aemb[akey[key]].reshape(-1,1)).reshape(()))
   sed=torch.stack(sd) if sd else torch.empty(0,device=dev);sea=torch.stack(sa) if sa else torch.empty(0,device=dev)
   vectors['Frozen-iKnow-05b'][ci]=joint(base[ci],ed,kappa,None)
   vectors['A_iKnow-TopP5-Control'][ci]=joint(base[ci],ed,kappa,P)
   vectors['B_Text-only'][ci]=joint(base[ci],ea,kappa,P)
   vectors['C_Fusion-only'][ci]=hier(base[ci],ed,kappa,P)
   vectors['D_Selector-only'][ci]=joint(base[ci],sed,kappa,P)
   vectors['E_Text+Fusion'][ci]=hier(base[ci],ea,kappa,P)
   vectors['F_Text+Selector'][ci]=joint(base[ci],sea,kappa,P)
   vectors['G_Fusion+Selector'][ci]=hier(base[ci],sed,kappa,P)
   vectors['H_Full'][ci]=hier(base[ci],sea,kappa,P)
  rr={m:rank(vectors[m],s['true_indices']) for m in METHODS}
  for m in METHODS:ranks[m].append(rr[m])
  rows.append({'sample_index':i,'audio_path':ap,'true_indices':[int(x) for x in s['true_indices']],'seed':sample_seed,'topk':top,'selected_relation':rel,'ranks':rr})
  all_scores.append(torch.stack([vectors[m] for m in METHODS]).cpu().numpy())
  if (i+1)%50==0:atom(out/'progress.json',{'completed':False,'done':i+1,'total':len(samples)})
 met={m:metrics(ranks[m]) for m in METHODS};np.savez_compressed(out/'predictions.npz',scores=np.asarray(all_scores),ranks=np.asarray([[x[m] for m in METHODS] for x in rows]),methods=METHODS)
 atom(out/'samples.json',rows);atom(out/'metrics.json',met);atom(out/'protocol.json',{'hop':1,'K':5,'M':3,'P':5,'R':1,'alpha':.5,'kappa':100,'dynamic_alpha':False,'second_hop':False,'selector':'Task18C Consensus-Margin-Top1 frozen per sample','branch_isolation':True,'methods':METHODS})
 lines=['method,Hit@1,Hit@3,Hit@5,MRR']+[f"{m},{met[m]['Hit@1']:.8f},{met[m]['Hit@3']:.8f},{met[m]['Hit@5']:.8f},{met[m]['MRR']:.8f}" for m in METHODS];(out/'metrics.csv').write_text('\n'.join(lines)+'\n')
 atom(out/'progress.json',{'completed':True,'done':len(samples),'total':len(samples)});print(json.dumps(met,indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('dataset');a=p.parse_args();main(a.dataset)
