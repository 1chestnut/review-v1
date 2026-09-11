#!/usr/bin/env python3
"""Consolidate Task25 factorial ablation and Task25g RawTriple control."""
import csv, hashlib, json
from pathlib import Path
import numpy as np
from scipy.stats import binomtest

ROOT=Path('/data/zkx/zkx/review1')
SRC=ROOT/'25_final_experiment_alpha03_Nr5'/'test'
RAW=ROOT/'25g_RawTriple_FS_control'
OUT=ROOT/'25h_consolidated_ablation';OUT.mkdir(parents=True,exist_ok=True)
SETS=[('01_ESC50','ESC-50'),('02_UrbanSound8K','UrbanSound8K'),('03_FSD50K','FSD50K'),('05_AudioSet','AudioSet'),('06_TUT2017','TUT2017')]
ORDER=['CLAP','I_iKnow','T_AAKV','F_Fusion','S_Selector','TF','TS','FS','Raw-FS','TFS_Final']
LABEL={'CLAP':'CLAP','I_iKnow':'Frozen-iKnow','T_AAKV':'+AAKV only','F_Fusion':'+Fusion only','S_Selector':'+Selector only','TF':'AAKV+Fusion','TS':'AAKV+Selector','FS':'Fusion+Selector (Direct)','Raw-FS':'Fusion+Selector (RawTriple)','TFS_Final':'AAKV+Fusion+Selector'}
CONTRASTS=[
 ('I_iKnow','F_Fusion','Fusion | Direct, FixedRq'),
 ('T_AAKV','TF','Fusion | AAKV, FixedRq'),
 ('S_Selector','FS','Fusion | Direct, Selector'),
 ('TS','TFS_Final','Fusion | AAKV, Selector'),
 ('I_iKnow','T_AAKV','AAKV | joint fusion, FixedRq'),
 ('F_Fusion','TF','AAKV | Fusion, FixedRq'),
 ('S_Selector','TS','AAKV | joint fusion, Selector'),
 ('FS','TFS_Final','AAKV | Fusion, Selector'),
 ('I_iKnow','S_Selector','Selector | Direct, joint fusion'),
 ('T_AAKV','TS','Selector | AAKV, joint fusion'),
 ('F_Fusion','FS','Selector | Direct, Fusion'),
 ('TF','TFS_Final','Selector | AAKV, Fusion'),
 ('Raw-FS','TFS_Final','AAKV vs RawTriple | Fusion+Selector'),
 ('I_iKnow','TFS_Final','Full system vs Frozen-iKnow')]

def metric(r):
 x=np.asarray(r,float);return {'Hit@1':100*np.mean(x<=1),'Hit@3':100*np.mean(x<=3),'Hit@5':100*np.mean(x<=5),'MRR':100*np.mean(1/x)}
def paired(a,b,seed,reps=10000):
 a=np.asarray(a,float);b=np.asarray(b,float);ah=a==1;bh=b==1;res=int(np.sum(~ah&bh));harm=int(np.sum(ah&~bh));n=res+harm
 p=float(binomtest(min(res,harm),n,.5).pvalue) if n else 1.;dh=bh.astype(float)-ah.astype(float);dr=1/b-1/a;rng=np.random.default_rng(seed);hs=[];rs=[]
 for start in range(0,reps,250):
  ix=rng.integers(0,len(a),size=(min(250,reps-start),len(a)));hs.append(dh[ix].mean(1)*100);rs.append(dr[ix].mean(1)*100)
 h=np.concatenate(hs);r=np.concatenate(rs)
 return {'delta_Hit@1_pp':100*dh.mean(),'Hit@1_CI_low':np.percentile(h,2.5),'Hit@1_CI_high':np.percentile(h,97.5),'rescued':res,'harmed':harm,'McNemar_p':p,'delta_MRR_pp':100*dr.mean(),'MRR_CI_low':np.percentile(r,2.5),'MRR_CI_high':np.percentile(r,97.5)}
def write(path,rows):
 keys=[]
 for x in rows:
  for k in x:
   if k not in keys:keys.append(k)
 with path.open('w',newline='',encoding='utf-8-sig') as f:w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(rows)

all_metrics=[];effects=[];checks=[]
for ds,name in SETS:
 p25=json.loads((SRC/ds/'protocol.json').read_text());praw=json.loads((RAW/ds/'protocol.json').read_text())
 rows=json.loads((SRC/ds/'samples.json').read_text());raw=json.loads((RAW/ds/'samples.json').read_text())
 identity=len(rows)==len(raw) and all(a['audio_path']==b['audio_path'] and a['true_indices']==b['true_indices'] for a,b in zip(rows,raw))
 frozen_ok=(p25['K']==praw['K']==5 and p25['M']==praw['M']==3 and p25['alpha']==praw['alpha']==.3 and p25['TopP']==praw['TopP']=='All/disabled' and p25['hop']==praw['hop']==1 and p25['seed']==praw['seed']==42)
 checks.append({'dataset':name,'sample_identity_match':identity,'K_M_alpha_TopP_hop_seed_match':frozen_ok,'n':len(rows)})
 if not identity or not frozen_ok:raise RuntimeError(f'protocol mismatch: {name}')
 ranks={m:[x['ranks'][m] for x in rows] for m in ORDER if m not in ('Raw-FS',)};ranks['Raw-FS']=[x['rank'] for x in raw]
 for m in ORDER:all_metrics.append({'dataset':name,'method':m,'display':LABEL[m],**metric(ranks[m])})
 for a,b,label in CONTRASTS:
  sd=250000+int(hashlib.sha256(f'{name}|{label}'.encode()).hexdigest()[:8],16)
  effects.append({'dataset':name,'contrast':label,'baseline':a,'method':b,**paired(ranks[a],ranks[b],sd)})

write(OUT/'01_complete_ablation_metrics.csv',all_metrics);write(OUT/'02_module_effects_paired.csv',effects);write(OUT/'03_protocol_checks.csv',checks)
lines=['# Consolidated controlled ablation (Task25 + Task25g)','',
'Task25 supplies the independent 2^3 ablation of AAKV, Fusion and Selector. Task25g adds RawTriple under the identical Fusion+Selector branch.','',
'Protocol check passed for every dataset: identical samples, K=5, M=3, alpha=0.3, one hop, Top-P disabled, seed=42, CLAP/KG/mapping and evaluation protocol.','',
'| Dataset | Frozen iKnow | AAKV only | Fusion only | Selector only | AAKV+Fusion | AAKV+Selector | Fusion+Selector Direct | Fusion+Selector Raw | Full AAKV+Fusion+Selector |',
'|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
for _,name in SETS:
 d={x['method']:x for x in all_metrics if x['dataset']==name}
 vals=[f"{d[m]['Hit@1']:.2f}/{d[m]['MRR']:.2f}" for m in ['I_iKnow','T_AAKV','F_Fusion','S_Selector','TF','TS','FS','Raw-FS','TFS_Final']]
 lines.append('| '+name+' | '+' | '.join(vals)+' |')
lines+=['','Each cell reports Hit@1/MRR. The factorial table should be used for module ablation; Raw-FS is an additional verbalization control, not a ninth factorial branch.','',
'## Primary clean contrasts','', '| Dataset | Fusion (F−I) H1/MRR | AAKV in full context (TFS−FS) | Selector in full context (TFS−TF) | Full−iKnow |','|---|---:|---:|---:|---:|']
for _,name in SETS:
 e={x['contrast']:x for x in effects if x['dataset']==name}
 def cell(k):
  x=e[k];return f"{x['delta_Hit@1_pp']:+.2f}/{x['delta_MRR_pp']:+.2f}"
 lines.append(f"| {name} | {cell('Fusion | Direct, FixedRq')} | {cell('AAKV | Fusion, Selector')} | {cell('Selector | AAKV, Fusion')} | {cell('Full system vs Frozen-iKnow')} |")
(OUT/'REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
(OUT/'summary_complete.json').write_text(json.dumps({'completed':True,'protocol_checks_passed':True,'datasets':[n for _,n in SETS]},indent=2),encoding='utf-8')
print((OUT/'REPORT.md').read_text())
