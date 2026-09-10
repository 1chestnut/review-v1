import os
os.environ['CUBLAS_WORKSPACE_CONFIG']=':4096:8'
os.environ['PYTHONHASHSEED']='42'
import argparse, json, hashlib, random, importlib.util, time, csv
from pathlib import Path
import numpy as np
import torch
import torch.nn.functional as F
from scipy.stats import binomtest
from tqdm import tqdm

ROOT=Path(__file__).resolve().parent
BASE=ROOT.parent
METHODS=['CLAP','A','B','C','D']
PAIRS=[('D','A'),('B','A'),('C','A'),('D','B'),('D','C')]
def digest(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,x):
 p=Path(p); t=p.with_suffix('.tmp'); t.write_text(json.dumps(x,ensure_ascii=False,indent=2)); t.replace(p)
def seed(s):
 random.seed(s); np.random.seed(s); torch.manual_seed(s); torch.cuda.manual_seed_all(s)
def module(p):
 s=importlib.util.spec_from_file_location('frozen_runtime',p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
def pool(v): return (torch.logsumexp(100*v,0)-np.log(v.numel()))/100
def joint(b,v): return pool(torch.cat([b.reshape(1),v])) if v.numel() else b
def ours(b,v,a):
 if not v.numel(): return b
 ids=torch.argsort(v,descending=True,stable=True)[:5]
 return a*b+(1-a)*pool(v[ids])
def holm(ps):
 order=np.argsort(ps); out=np.zeros(len(ps)); last=0
 for i,j in enumerate(order): last=max(last,min(1,(len(ps)-i)*ps[j])); out[j]=last
 return out.tolist()
def stats(ranks,out):
 r=np.asarray(ranks); hit=(r==1).astype(float); rr=1/r
 metrics={m:{'Hit@1':float(100*np.mean(r[:,i]<=1)),'Hit@3':float(100*np.mean(r[:,i]<=3)),
 'Hit@5':float(100*np.mean(r[:,i]<=5)),'MRR':float(100*np.mean(rr[:,i]))} for i,m in enumerate(METHODS)}
 contrasts=[]
 for x,y in PAIRS:
  i=METHODS.index(x); j=METHODS.index(y)
  gain=int(np.sum((hit[:,i]==1)&(hit[:,j]==0))); loss=int(np.sum((hit[:,i]==0)&(hit[:,j]==1)))
  contrasts.append({'comparison':x+'-'+y,'gain_count':gain,'loss_count':loss,'mcnemar_p':float(binomtest(gain,gain+loss,.5).pvalue) if gain+loss else 1.})
 coefficients=[]
 for x,y in PAIRS:
  c=np.zeros(5); c[METHODS.index(x)]=1;c[METHODS.index(y)]=-1;coefficients.append(c)
 coefficients.append(np.array([0,1,-1,-1,1]))
 vals=np.stack([hit@np.array(coefficients).T,rr@np.array(coefficients).T],axis=-1)*100
 rng=np.random.default_rng(42); boots=np.empty((10000,6,2))
 for k in range(10000): boots[k]=vals[rng.integers(0,len(r),len(r))].mean(0)
 ci=np.quantile(boots,[.025,.975],axis=0); means=vals.mean(0)
 contrasts.append({'comparison':'D-B-C+A'})
 for k,row in enumerate(contrasts):
  for j,name in enumerate(['Hit@1','MRR']):row[name]={'difference_pp':float(means[k,j]),'paired_bootstrap95':ci[:,k,j].tolist()}
 for row,p in zip(contrasts,holm([x['mcnemar_p'] for x in contrasts[:5]])):row['holm_p_within_dataset']=p
 save(out/'statistics.json',{'n_clips':len(r),'replicates':10000,'seed':42,'unit':'audio clip; assumes independent clips; source-recording clustering not assessed',
 'conditional_on':'frozen CLAP, KG, generated texts and one deterministic crop per clip','contrasts':contrasts})
 save(out/'metrics.json',metrics)
 with open(out/'metrics.csv','w') as f:
  w=csv.writer(f);w.writerow(['method','Hit@1','Hit@3','Hit@5','MRR'])
  for m in METHODS:w.writerow([m]+[metrics[m][x] for x in ['Hit@1','Hit@3','Hit@5','MRR']])

def main(ds):
 out=ROOT/ds;out.mkdir(exist_ok=True)
 snap=out/'frozen_inputs';snap.mkdir(exist_ok=True)
 src=BASE/'06_onehop-text-verbalization-audit'/ds
 inputs={'runtime.py':src/'iknow_runtime.py','config.json':src/'config.json','triples.json':src/'cache/triples_and_texts.json',
 'aakv.json':BASE/'10_hard-prefix-pilot'/ds/'prompts/qwen_generation_audit.json',
 'mapping.json':src.parent/'entity_mapping_v2.json'}
 hashes={}
 for name,p in inputs.items():
  target=snap/name
  if target.exists(): assert digest(target)==digest(p),'Source changed: '+str(p)
  else: target.write_bytes(p.read_bytes())
  hashes[name]=digest(target)
 cfg=json.loads((snap/'config.json').read_text());kg=json.loads((snap/'triples.json').read_text());q=json.loads((snap/'aakv.json').read_text())
 assert cfg['top_k']==5 and cfg['top_m']==3 and cfg['logit_scale']==100
 assert q['completed'] and 'Begin the sentence with exactly' in q['system_prompt']
 assert kg['signature']['mapping_sha256']==hashes['mapping.json']
 qrows={(x['class_id'],x['triple_id']):x for x in q['rows']}
 assert len(qrows)==sum(len(c['triples']) for c in kg['classes'])
 texts=[];indices=[]
 for ci,c in enumerate(kg['classes']):
  ix={'direct':[],'aakv':[]}
  for ti,t in enumerate(c['triples']):
   qr=qrows[ci,ti]
   assert all(t[k]==qr[k] for k in ['head','relation','tail'])
   assert qr['verification_outcome'] in ['accepted_first','accepted_repair','universal_fallback']
   for key,txt in [('direct',t['direct']),('aakv',qr['qwen_verified'])]: ix[key].append(len(texts));texts.append(txt)
  indices.append(ix)
 seed(42);torch.use_deterministic_algorithms(True);torch.backends.cudnn.benchmark=False;torch.backends.cudnn.deterministic=True
 torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
 base=module(snap/'runtime.py');clap=base.CLAP(version='2023',use_cuda=True);clap.clap.eval()
 dataset=base.load_dataset();samples=list(base.iter_samples(dataset));labels=list(dataset['label_classes'])
 assert labels==kg['signature']['labels']
 manifest=[{'audio_path':s['audio_path'],'true_indices':[int(x) for x in s['true_indices']],
 'size':Path(s['audio_path']).stat().st_size,'mtime_ns':Path(s['audio_path']).stat().st_mtime_ns} for s in samples]
 save(out/'manifest.json',manifest)
 save(out/'protocol.json',{'hashes':hashes,'config':cfg,'seed':42,'crop':'original CLAP random crop with stable path-derived per-sample seed',
 'A':'Direct + joint NormLSE100, all evidence','B':'Direct + Top5 + dynamic alpha','C':'AAKV + joint NormLSE100, all evidence','D':'AAKV + Top5 + dynamic alpha',
 'alpha':[.4,.8],'eval':True,'torch':torch.__version__,'numpy':np.__version__,'AAKV_prompt':q['system_prompt'],'AAKV_audit':q['audit']})
 with torch.inference_mode():
  label_emb=F.normalize(base.get_safe_text_embeddings(clap,labels,'cuda'),dim=-1)
  evidence_emb=F.normalize(base.get_safe_text_embeddings(clap,texts,'cuda'),dim=-1)
  torch.save({'labels':label_emb.cpu(),'evidence':evidence_emb.cpu(),'texts':texts,'indices':indices},out/'text_embeddings.pt')
  audio_cache=out/'audio_cache';audio_cache.mkdir(exist_ok=True)
  rankrows=[];records=[];fullscores=[];fullorders=[]
  for i,s in enumerate(tqdm(samples,desc=ds,mininterval=10)):
   assert s['true_indices'],'Missing labels'
   cache=audio_cache/f'{i:06d}.pt'
   sample_seed=int(hashlib.sha256(('42|'+s['audio_path']).encode()).hexdigest()[:8],16)
   if cache.exists():audio=torch.load(cache,map_location='cuda')
   else:
    seed(sample_seed)
    audio=F.normalize(base.to_tensor(clap.get_audio_embeddings([s['audio_path']])).to('cuda').float(),dim=-1)
    torch.save(audio.cpu(),cache)
   b=(audio@label_emb.T).squeeze(0); e=(audio@evidence_emb.T).squeeze(0)
   top=torch.argsort(b,descending=True)[:5].tolist();alpha=float(np.clip(.4+.4*float(b.max()),.4,.8))
   vectors={m:b.clone() for m in METHODS}
   for c in top:
    for form,jm,om in [('direct','A','B'),('aakv','C','D')]:
     ev=e[indices[c][form]]
     vectors[jm][c]=joint(b[c],ev);vectors[om][c]=ours(b[c],ev,alpha)
   orders=torch.stack([torch.argsort(vectors[m],descending=True) for m in METHODS]).cpu().numpy()
   ranks=[min(int(np.where(order==y)[0][0])+1 for y in s['true_indices']) for order in orders]
   rankrows.append(ranks);fullorders.append(orders);fullscores.append(torch.stack([vectors[m] for m in METHODS]).cpu().numpy())
   records.append({'sample_index':i,'audio_path':s['audio_path'],'true_indices':s['true_indices'],'seed':sample_seed,'alpha':alpha,'topk':top,'ranks':dict(zip(METHODS,ranks))})
   if i%50==0:save(out/'progress.json',{'completed':False,'phase':'inference','done':i+1,'total':len(samples)})
  np.savez_compressed(out/'predictions.npz',scores=np.asarray(fullscores),orders=np.asarray(fullorders),ranks=np.asarray(rankrows),methods=METHODS)
  save(out/'samples.json',records)
 del clap;torch.cuda.empty_cache()
 save(out/'progress.json',{'completed':False,'phase':'statistics','done':len(samples),'total':len(samples)})
 stats(rankrows,out)
 save(out/'progress.json',{'completed':True,'phase':'complete','done':len(samples),'total':len(samples)})

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('dataset');a=p.parse_args();main(a.dataset)
