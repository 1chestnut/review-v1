import os
os.environ['CUBLAS_WORKSPACE_CONFIG']=':4096:8'
os.environ['PYTHONHASHSEED']='42'
import argparse, csv, json, math, random
from pathlib import Path
import numpy as np
import torch
from scipy.stats import binomtest
from tqdm import tqdm

ROOT=Path('/data/zkx/zkx/review1/17_formula_component_ablation')
SOURCE=ROOT.parent/'12_shared-abcd-statistics'
KAPPA=100.0; TOPK=5; P=5
METHODS=['CLAP','JointRaw-All','JointNorm-All','JointNorm-Top5',
         'TwoStage-a0.3','TwoStage-a0.5','TwoStage-a0.7','TwoStage-Dynamic']
PAIRS=[('JointNorm-All','JointRaw-All'),
       ('JointNorm-Top5','JointNorm-All'),
       ('TwoStage-a0.3','JointNorm-Top5'),
       ('TwoStage-a0.5','JointNorm-Top5'),
       ('TwoStage-a0.7','JointNorm-Top5'),
       ('TwoStage-Dynamic','JointNorm-Top5'),
       ('TwoStage-Dynamic','TwoStage-a0.3'),
       ('TwoStage-Dynamic','TwoStage-a0.5'),
       ('TwoStage-Dynamic','TwoStage-a0.7')]

def save(p,x):
 p=Path(p);t=p.with_suffix(p.suffix+'.tmp');t.write_text(json.dumps(x,ensure_ascii=False,indent=2));t.replace(p)
def seed(s=42):
 random.seed(s);np.random.seed(s);torch.manual_seed(s);torch.cuda.manual_seed_all(s)
def lse(v): return torch.logsumexp(KAPPA*v,0)/KAPPA
def norm_lse(v): return (torch.logsumexp(KAPPA*v,0)-math.log(v.numel()))/KAPPA
def top(v): return v[torch.argsort(v,descending=True,stable=True)[:P]]
def metric(r):
 return {'Hit@1':float(100*np.mean(r<=1)),'Hit@3':float(100*np.mean(r<=3)),
         'Hit@5':float(100*np.mean(r<=5)),'MRR':float(100*np.mean(1/r))}

def statistics(ranks,out):
 rng=np.random.default_rng(42);rows=[]
 for x,y in PAIRS:
  i,j=METHODS.index(x),METHODS.index(y);rx,ry=ranks[:,i],ranks[:,j]
  dh=100*((rx<=1).astype(float)-(ry<=1).astype(float));dr=100*(1/rx-1/ry)
  boot=np.empty((10000,2))
  for z in range(10000):
   ix=rng.integers(0,len(rx),len(rx));boot[z]=[dh[ix].mean(),dr[ix].mean()]
  gain=int(np.sum((rx==1)&(ry!=1)));loss=int(np.sum((rx!=1)&(ry==1)))
  rows.append({'comparison':x+' - '+y,'delta_Hit@1_pp':float(dh.mean()),
   'Hit@1_CI95':np.quantile(boot[:,0],[.025,.975]).tolist(),'delta_MRR_pp':float(dr.mean()),
   'MRR_CI95':np.quantile(boot[:,1],[.025,.975]).tolist(),'wrong_to_right':gain,
   'right_to_wrong':loss,'mcnemar_p':float(binomtest(gain,gain+loss,.5).pvalue) if gain+loss else 1.,
   'rank_improved':int(np.sum(rx<ry)),'rank_worsened':int(np.sum(rx>ry))})
 save(out/'statistics.json',{'bootstrap':10000,'seed':42,'paired_by_audio':True,'rows':rows});return rows

@torch.inference_mode()
def main(ds):
 seed();torch.use_deterministic_algorithms(True);torch.backends.cudnn.benchmark=False
 torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
 src=SOURCE/ds;out=ROOT/ds;out.mkdir(parents=True,exist_ok=True)
 te=torch.load(src/'text_embeddings.pt',map_location='cuda');labels=te['labels'].to('cuda');evidence=te['evidence'].to('cuda');indices=te['indices']
 samples=json.loads((src/'samples.json').read_text());ranks=[];scores=[];records=[]
 for si,s in enumerate(tqdm(samples,desc=ds,mininterval=10)):
  audio=torch.load(src/'audio_cache'/f'{si:06d}.pt',map_location='cuda')
  b=(audio@labels.T).squeeze(0);e=(audio@evidence.T).squeeze(0)
  topclasses=torch.argsort(b,descending=True)[:TOPK].tolist();dynamic=float(np.clip(.4+.4*float(b.max()),.4,.8))
  vectors={m:b.clone() for m in METHODS}
  for ci in topclasses:
   ev=e[indices[ci]['aakv']]
   if not ev.numel(): continue
   ev5=top(ev);joint_all=torch.cat([b[ci].reshape(1),ev]);joint5=torch.cat([b[ci].reshape(1),ev5])
   vectors['JointRaw-All'][ci]=lse(joint_all)
   vectors['JointNorm-All'][ci]=norm_lse(joint_all)
   vectors['JointNorm-Top5'][ci]=norm_lse(joint5)
   kg=norm_lse(ev5)
   for a in [.3,.5,.7]: vectors[f'TwoStage-a{a}'][ci]=a*b[ci]+(1-a)*kg
   vectors['TwoStage-Dynamic'][ci]=dynamic*b[ci]+(1-dynamic)*kg
  arr=torch.stack([vectors[m] for m in METHODS]);orders=torch.argsort(arr,dim=1,descending=True).cpu().numpy()
  true=[int(x) for x in s['true_indices']];rr=[min(int(np.where(o==y)[0][0])+1 for y in true) for o in orders]
  ranks.append(rr);scores.append(arr.cpu().numpy());records.append({'sample_index':si,'audio_path':s['audio_path'],
   'true_indices':true,'dynamic_alpha':dynamic,'ranks':dict(zip(METHODS,rr))})
  if (si+1)%100==0:save(out/'progress.json',{'completed':False,'done':si+1,'total':len(samples)})
 ranks=np.asarray(ranks);metrics={m:metric(ranks[:,i]) for i,m in enumerate(METHODS)}
 save(out/'metrics.json',metrics);save(out/'samples.json',records)
 with (out/'metrics.csv').open('w',newline='',encoding='utf-8') as f:
  w=csv.writer(f);w.writerow(['method','Hit@1','Hit@3','Hit@5','MRR'])
  for m in METHODS:w.writerow([m]+[metrics[m][q] for q in ['Hit@1','Hit@3','Hit@5','MRR']])
 stats=statistics(ranks,out);np.savez_compressed(out/'predictions.npz',scores=np.asarray(scores),ranks=ranks,methods=np.asarray(METHODS))
 # Task12 D must equal this dynamic column exactly, otherwise the ablation is not controlled.
 old=np.load(src/'predictions.npz',allow_pickle=True);om=[str(x) for x in old['methods']];oldr=old['ranks'][:,om.index('D')]
 assert np.array_equal(oldr,ranks[:,METHODS.index('TwoStage-Dynamic')]),'Dynamic result differs from Task12 D'
 save(out/'protocol.json',{'purpose':'Separate cardinality normalization, Top-P, two-stage fusion and dynamic alpha',
  'frozen':{'source':'Task12','text':'AAKV','TopK':TOPK,'P':P,'kappa':KAPPA,'relations_K_M_audio_text_and_samples':'unchanged'},
  'methods':METHODS,'formulas':{
   'JointRaw-All':'LSE([base,evidence_all])',
   'JointNorm-All':'LSE([base,evidence_all])-log(n+1)/kappa',
   'JointNorm-Top5':'same joint normalized aggregation after retaining top-5 knowledge evidence',
   'TwoStage':'NormLSE(top-5 knowledge) followed by alpha*base+(1-alpha)*knowledge',
   'Dynamic-alpha':'clip(0.4+0.4*max_base,0.4,0.8)'},
  'consistency':'TwoStage-Dynamic ranks exactly equal Task12 D'})
 save(out/'progress.json',{'completed':True,'done':len(samples),'total':len(samples)})
 print(json.dumps({'dataset':ds,'metrics':metrics,'statistics':stats},indent=2))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('dataset');a=p.parse_args();main(a.dataset)
