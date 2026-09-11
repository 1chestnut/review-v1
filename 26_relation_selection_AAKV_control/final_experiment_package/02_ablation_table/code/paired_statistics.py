#!/usr/bin/env python3
"""Task25(c): paired bootstrap, exact McNemar, and prediction transitions."""
import csv, hashlib, json
from pathlib import Path
import numpy as np
from scipy.stats import binomtest

ROOT=Path('/data/zkx/zkx/review1')
SOURCE=ROOT/'25_final_experiment_alpha03_Nr5'/'test'
OUT=ROOT/'25c_task25_paired_statistics'
DATASETS=[('01_ESC50','ESC-50'),('02_UrbanSound8K','UrbanSound8K'),('03_FSD50K','FSD50K'),('05_AudioSet','AudioSet'),('06_TUT2017','TUT2017')]
PRIMARY=('I_iKnow','TFS_Final','Final-TFS - Frozen-iKnow')
CONTRASTS=[
 ('I_iKnow','T_AAKV','T only - iKnow'),('I_iKnow','F_Fusion','F only - iKnow'),('I_iKnow','S_Selector','S only - iKnow'),
 ('TF','TFS_Final','add S to TF'),('TS','TFS_Final','add F to TS'),('FS','TFS_Final','add T to FS')]

def bootstrap(dh,dr,seed,reps=10000,chunk=250):
 rng=np.random.default_rng(seed);n=len(dh);hs=[];rs=[]
 for start in range(0,reps,chunk):
  z=min(chunk,reps-start);idx=rng.integers(0,n,size=(z,n));hs.append(dh[idx].mean(1)*100);rs.append(dr[idx].mean(1)*100)
 return np.percentile(np.concatenate(hs),[2.5,97.5]),np.percentile(np.concatenate(rs),[2.5,97.5])

def holm(vals):
 p=np.asarray(vals,float);order=np.argsort(p);q=np.maximum.accumulate((len(p)-np.arange(len(p)))*p[order]);q=np.minimum(q,1);out=np.empty_like(q);out[order]=q;return out

def compare(ds,name,rows,a,b,label,transitions=False):
 ra=np.asarray([x['ranks'][a] for x in rows],float);rb=np.asarray([x['ranks'][b] for x in rows],float)
 ah=(ra==1).astype(float);bh=(rb==1).astype(float);ar=1/ra;br=1/rb
 rescued=int(np.sum((ah==0)&(bh==1)));harmed=int(np.sum((ah==1)&(bh==0)));disc=rescued+harmed
 p=float(binomtest(min(rescued,harmed),disc,.5).pvalue) if disc else 1.
 seed=20260911+int(hashlib.sha256((name+'|'+label).encode()).hexdigest()[:8],16);hci,rci=bootstrap(bh-ah,br-ar,seed)
 result={'dataset':name,'n':len(rows),'comparison':label,'baseline':a,'method':b,'delta_Hit@1_pp':float((bh-ah).mean()*100),
  'Hit@1_CI95_low':float(hci[0]),'Hit@1_CI95_high':float(hci[1]),'wrong_to_correct':rescued,'correct_to_wrong':harmed,
  'net_rescued':rescued-harmed,'McNemar_exact_p':p,'delta_MRR_pp':float((br-ar).mean()*100),'MRR_CI95_low':float(rci[0]),'MRR_CI95_high':float(rci[1])}
 detail=[]
 if transitions:
  for i,x in enumerate(rows):
   state='wrong_to_correct' if not ah[i] and bh[i] else 'correct_to_wrong' if ah[i] and not bh[i] else 'both_correct' if ah[i] else 'both_wrong'
   detail.append({'dataset':name,'sample_index':x['sample_index'],'audio_path':x['audio_path'],'baseline_rank':int(ra[i]),'final_rank':int(rb[i]),'Hit@1_transition':state,'delta_reciprocal_rank':float(br[i]-ar[i])})
 return result,detail

OUT.mkdir(parents=True,exist_ok=True);primary=[];explore=[];trans=[]
for ds,name in DATASETS:
 rows=json.loads((SOURCE/ds/'samples.json').read_text(encoding='utf-8'))
 r,t=compare(ds,name,rows,*PRIMARY,True);primary.append(r);trans.extend(t)
 for a,b,label in CONTRASTS:
  r,_=compare(ds,name,rows,a,b,label,False);explore.append(r)

for family in (primary,explore):
 adj=holm([x['McNemar_exact_p'] for x in family])
 for x,q in zip(family,adj):
  x['McNemar_Holm_p_family']=float(q);x['McNemar_significant_Holm_0.05']=bool(q<.05)
  x['Hit@1_CI_excludes_zero']=bool(x['Hit@1_CI95_low']>0 or x['Hit@1_CI95_high']<0);x['MRR_CI_excludes_zero']=bool(x['MRR_CI95_low']>0 or x['MRR_CI95_high']<0)
for path,data in [(OUT/'01_primary_final_vs_iknow.csv',primary),(OUT/'02_module_contrasts.csv',explore),(OUT/'03_primary_sample_transitions.csv',trans)]:
 with path.open('w',newline='',encoding='utf-8-sig') as f:w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
protocol={'source':'Task25 independently computed branches','development_set':'DCASE17-T4 (excluded)','test_sets':5,'primary_comparison':PRIMARY[2],
 'bootstrap':{'paired':True,'repetitions':10000,'unit':'audio sample','CI':'percentile 95%'},'McNemar':'exact two-sided on paired Hit@1 outcomes',
 'multiplicity':{'primary':'Holm across five datasets','module_contrasts':'Holm across all 30 exploratory tests'},'seed_rule':'deterministic hash of dataset and contrast','training_repeats':'not applicable: frozen deterministic inference; uncertainty is over test samples'}
(OUT/'protocol.json').write_text(json.dumps(protocol,ensure_ascii=False,indent=2),encoding='utf-8')
lines=['# Task25(c) paired statistics','','Primary comparison: Final-TFS versus frozen iKnow. DCASE is not included.','','| Dataset | dHit@1 [95% CI] | rescued/harmed | exact p | Holm p | dMRR [95% CI] |','|---|---:|---:|---:|---:|---:|']
for x in primary:lines.append(f"| {x['dataset']} | {x['delta_Hit@1_pp']:+.3f} [{x['Hit@1_CI95_low']:+.3f}, {x['Hit@1_CI95_high']:+.3f}] | {x['wrong_to_correct']}/{x['correct_to_wrong']} | {x['McNemar_exact_p']:.4g} | {x['McNemar_Holm_p_family']:.4g} | {x['delta_MRR_pp']:+.3f} [{x['MRR_CI95_low']:+.3f}, {x['MRR_CI95_high']:+.3f}] |")
(OUT/'REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8');(OUT/'progress.json').write_text(json.dumps({'completed':True,'primary_rows':len(primary),'exploratory_rows':len(explore)},indent=2))
