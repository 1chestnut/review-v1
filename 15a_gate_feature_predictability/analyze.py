import csv, json, math
from pathlib import Path
from collections import Counter

import numpy as np
import torch
from sklearn.metrics import roc_auc_score, average_precision_score
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

ROOT=Path('/data/zkx/zkx/review1')
OUT=ROOT/'15a_gate_feature_predictability';OUT.mkdir(parents=True,exist_ok=True)
DATASETS=['01_ESC50','02_UrbanSound8K','03_FSD50K','04_DCASE17_T4','05_AudioSet','06_TUT2017']
FEATURE_DIRECTIONS={
 'neg_base_margin':1,'neg_first_margin':1,'base_entropy':1,'first_entropy':1,
 'top1_conflict':1,'js_divergence':1,'neg_evidence_support':1,
 'evidence_variance':1,'distribution_l1_change':1,'top1_score_change_abs':1,
}

def save(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
def probs(scores):
 z=100.0*scores;z=z-z.max(1,keepdims=True);e=np.exp(z);return e/e.sum(1,keepdims=True)
def entropy(p):return -np.sum(p*np.log(np.clip(p,1e-12,1)),axis=1)/np.log(p.shape[1])
def aucs(y,s):
 if len(np.unique(y))<2:return float('nan'),float('nan')
 return float(roc_auc_score(y,s)),float(average_precision_score(y,s))

all_ds=[];feature_rows=[];threshold_rows=[];dataset_summary=[]
for ds in DATASETS:
 t12=np.load(ROOT/'12_shared-abcd-statistics'/ds/'predictions.npz',allow_pickle=True)
 m12=[str(x) for x in t12['methods']];base=t12['scores'][:,m12.index('CLAP'),:].astype(np.float64)
 t14=np.load(ROOT/'14_aakv_mp_potential'/ds/'predictions.npz',allow_pickle=True)
 m14=[str(x) for x in t14['methods']];scores=t14['scores'].astype(np.float64);ranks=t14['ranks']
 first=scores[:,m14.index('1st-P5'),:]
 assert base.shape==first.shape and len(base)==len(ranks)
 p0=probs(base);p1=probs(first);mix=.5*(p0+p1)
 sort0=np.sort(base,axis=1);sort1=np.sort(first,axis=1)
 top0=base.argmax(1);top1=first.argmax(1);idx=np.arange(len(base))
 feats={
  'neg_base_margin':-(sort0[:,-1]-sort0[:,-2]),
  'neg_first_margin':-(sort1[:,-1]-sort1[:,-2]),
  'base_entropy':entropy(p0),'first_entropy':entropy(p1),
  'top1_conflict':(top0!=top1).astype(float),
  'js_divergence':.5*np.sum(p0*np.log(np.clip(p0/mix,1e-12,None)),axis=1)+.5*np.sum(p1*np.log(np.clip(p1/mix,1e-12,None)),axis=1),
  'distribution_l1_change':np.sum(np.abs(p1-p0),axis=1),
  'top1_score_change_abs':np.abs(first[idx,top1]-base[idx,top1]),
 }
 # One-hop evidence quality for the one-hop predicted top class.
 text=torch.load(ROOT/'12_shared-abcd-statistics'/ds/'text_embeddings.pt',map_location='cpu')
 emb=text['evidence'].float();indices=text['indices'];support=np.empty(len(base));variance=np.empty(len(base))
 audio_root=ROOT/'12_shared-abcd-statistics'/ds/'audio_cache'
 for i,c in enumerate(top1):
  audio=torch.load(audio_root/f'{i:06d}.pt',map_location='cpu').float();ids=indices[int(c)]['aakv']
  values=(audio@emb[ids].T).flatten().numpy() if ids else np.asarray([],dtype=float)
  support[i]=values.max() if len(values) else -1.;variance[i]=values.var() if len(values) else 0.
 feats['neg_evidence_support']=-support;feats['evidence_variance']=variance
 bidx=m14.index('1st-P5');fixed_idx=m14.index('AAKV-M1-P5')
 grid_idx=[m14.index(f'AAKV-M{m}-P5') for m in [1,3,5]]
 y_fixed_benefit=(ranks[:,fixed_idx]<ranks[:,bidx]).astype(int)
 y_fixed_harm=(ranks[:,fixed_idx]>ranks[:,bidx]).astype(int)
 y_any_benefit=(ranks[:,grid_idx].min(1)<ranks[:,bidx]).astype(int)
 X=np.column_stack([feats[k] for k in FEATURE_DIRECTIONS])
 np.savez_compressed(OUT/f'{ds}_features.npz',X=X,feature_names=np.asarray(list(FEATURE_DIRECTIONS)),
   y_any_benefit=y_any_benefit,y_fixed_benefit=y_fixed_benefit,y_fixed_harm=y_fixed_harm,
   rank_first=ranks[:,bidx],rank_fixed=ranks[:,fixed_idx])
 dataset_summary.append({'dataset':ds,'n':len(base),'any_benefit':int(y_any_benefit.sum()),
  'fixed_benefit':int(y_fixed_benefit.sum()),'fixed_harm':int(y_fixed_harm.sum()),
  'top1_conflict':int(feats['top1_conflict'].sum())})
 for name,s in feats.items():
  for target,y in [('any_M_P5_benefit',y_any_benefit),('fixed_M1_P5_benefit',y_fixed_benefit),('fixed_M1_P5_harm',y_fixed_harm)]:
   au,ap=aucs(y,s);feature_rows.append({'dataset':ds,'feature':name,'target':target,'AUROC':au,'AUPRC':ap,'prevalence':float(y.mean())})
  # Post-hoc coverage curves. Higher feature score means more likely to trigger.
  order=np.argsort(-s,kind='stable')
  for budget in [.1,.2,.3,.5]:
   n=max(1,int(round(len(base)*budget)));trigger=np.zeros(len(base),bool);trigger[order[:n]]=True
   rescue=int(np.sum(trigger & (y_fixed_benefit==1)));harm=int(np.sum(trigger & (y_fixed_harm==1)))
   threshold_rows.append({'dataset':ds,'feature':name,'trigger_budget':budget,'trigger_n':n,
    'fixed_rescue_covered':rescue,'fixed_rescue_recall':float(rescue/max(1,y_fixed_benefit.sum())),
    'fixed_harm_triggered':harm,'harm_per_trigger':float(harm/n),
    'any_M_rescue_recall':float(np.sum(trigger&(y_any_benefit==1))/max(1,y_any_benefit.sum()))})
 all_ds.append((ds,X,y_any_benefit,y_fixed_benefit,y_fixed_harm))

# Leave-one-dataset-out transfer analysis. Each held-out dataset contributes no labels to its router.
lodo=[]
for held,Xtest,ytest,fb,fh in all_ds:
 train=[x for x in all_ds if x[0]!=held];Xtr=np.concatenate([x[1] for x in train]);ytr=np.concatenate([x[2] for x in train])
 model=make_pipeline(StandardScaler(),LogisticRegression(class_weight='balanced',max_iter=2000,random_state=42))
 model.fit(Xtr,ytr);pr=model.predict_proba(Xtest)[:,1];au,ap=aucs(ytest,pr)
 for budget in [.1,.2,.3,.5]:
  n=max(1,int(round(len(pr)*budget)));ix=np.argsort(-pr)[:n];trigger=np.zeros(len(pr),bool);trigger[ix]=True
  lodo.append({'held_out_dataset':held,'AUROC':au,'AUPRC':ap,'benefit_prevalence':float(ytest.mean()),
    'trigger_budget':budget,'any_benefit_recall':float(np.sum(trigger&(ytest==1))/max(1,ytest.sum())),
    'fixed_benefit_covered':int(np.sum(trigger&(fb==1))),'fixed_harm_triggered':int(np.sum(trigger&(fh==1)))})

def write_csv(name,rows):
 with (OUT/name).open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
write_csv('feature_predictability.csv',feature_rows);write_csv('threshold_budget_curves.csv',threshold_rows);write_csv('lodo_router.csv',lodo)
save(OUT/'dataset_summary.json',dataset_summary)
save(OUT/'protocol.json',{
 'analysis_only':True,'no_new_CLAP_or_KG_inference':True,'softmax_scale':100,
 'primary_target':'any of AAKV M2={1,3,5}, P=5 improves true-label rank over 1st-P5',
 'fixed_target':'AAKV-M1-P5 improves/worsens true-label rank over 1st-P5',
 'features_available_before_second_hop':list(FEATURE_DIRECTIONS),
 'warning':'Ground truth defines analysis labels only. No test-set threshold or model may be reused as a final gate.',
 'lodo':'train on five datasets, evaluate feature transfer on one held-out dataset; diagnostic only'})
print(json.dumps({'dataset_summary':dataset_summary,'lodo':lodo},indent=2))
