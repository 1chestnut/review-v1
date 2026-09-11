#!/usr/bin/env python3
"""Final paired statistics for frozen alpha=.3, Nr=5 on five test datasets."""
import csv, hashlib, json
from pathlib import Path
import numpy as np
from scipy.stats import binomtest

ROOT=Path('/data/zkx/zkx/review1')
BASE=ROOT/'21_noTopP_factorial_vs_frozen_iKnow'
FINAL=ROOT/'23D_five_test_extended_Nr_sensitivity'
OUT=ROOT/'24_final_statistics_alpha03_Nr5'
METHOD='TFS_alpha0.3_Nr5'; BASELINE='I_Frozen-iKnow-05b'
DATASETS=[('01_ESC50','ESC-50'),('02_UrbanSound8K','UrbanSound8K'),('03_FSD50K','FSD50K'),
          ('05_AudioSet','AudioSet'),('06_TUT2017','TUT2017')]

def bootstrap(dh,dr,seed,reps=10000,chunk=250):
    rng=np.random.default_rng(seed);n=len(dh);hs=[];rs=[]
    for start in range(0,reps,chunk):
        z=min(chunk,reps-start);idx=rng.integers(0,n,size=(z,n))
        hs.append(dh[idx].mean(1)*100);rs.append(dr[idx].mean(1)*100)
    return np.percentile(np.concatenate(hs),[2.5,97.5]),np.percentile(np.concatenate(rs),[2.5,97.5])

def holm(values):
    p=np.asarray(values,float);order=np.argsort(p);q=np.maximum.accumulate((len(p)-np.arange(len(p)))*p[order]);q=np.minimum(q,1);out=np.empty_like(q);out[order]=q;return out

OUT.mkdir(parents=True,exist_ok=True);results=[];transitions=[]
for ds,name in DATASETS:
    br=json.loads((BASE/ds/'samples.json').read_text(encoding='utf-8'))
    fr=json.loads((FINAL/ds/'samples.json').read_text(encoding='utf-8'))
    bm={x['audio_path']:x for x in br};fm={x['audio_path']:x for x in fr}
    if set(bm)!=set(fm):raise RuntimeError(f'{name}: sample sets differ')
    paths=[x['audio_path'] for x in fr]
    b=np.asarray([bm[p]['ranks'][BASELINE] for p in paths],float)
    f=np.asarray([fm[p]['ranks'][METHOD] for p in paths],float)
    bh=(b==1).astype(float);fh=(f==1).astype(float);brcp=1/b;frcp=1/f
    rescued=int(np.sum((bh==0)&(fh==1)));harmed=int(np.sum((bh==1)&(fh==0)));disc=rescued+harmed
    p=float(binomtest(min(rescued,harmed),disc,.5).pvalue) if disc else 1.
    seed=2026+int(hashlib.sha256(name.encode()).hexdigest()[:8],16)
    hci,rci=bootstrap(fh-bh,frcp-brcp,seed)
    results.append({'dataset':name,'n':len(paths),'comparison':'Final-TFS - frozen-iKnow',
      'alpha':.3,'Nr':5,'delta_Hit@1_pp':float((fh-bh).mean()*100),'Hit@1_CI95_low':float(hci[0]),'Hit@1_CI95_high':float(hci[1]),
      'wrong_to_correct':rescued,'correct_to_wrong':harmed,'net_rescued':rescued-harmed,'McNemar_exact_p':p,
      'delta_MRR_pp':float((frcp-brcp).mean()*100),'MRR_CI95_low':float(rci[0]),'MRR_CI95_high':float(rci[1])})
    for i,path in enumerate(paths):
        status='wrong_to_correct' if not bh[i] and fh[i] else 'correct_to_wrong' if bh[i] and not fh[i] else 'both_correct' if bh[i] else 'both_wrong'
        transitions.append({'dataset':name,'sample_index':i,'audio_path':path,'iKnow_rank':int(b[i]),'final_rank':int(f[i]),'Hit@1_transition':status,'delta_reciprocal_rank':float(frcp[i]-brcp[i])})

adj=holm([x['McNemar_exact_p'] for x in results])
for x,q in zip(results,adj):
    x['McNemar_Holm_p_5']=float(q);x['McNemar_significant_Holm_0.05']=bool(q<.05)
    x['Hit@1_CI_excludes_zero']=bool(x['Hit@1_CI95_low']>0 or x['Hit@1_CI95_high']<0)
    x['MRR_CI_excludes_zero']=bool(x['MRR_CI95_low']>0 or x['MRR_CI95_high']<0)
with (OUT/'final_statistics.csv').open('w',newline='',encoding='utf-8-sig') as f:
    w=csv.DictWriter(f,fieldnames=list(results[0]));w.writeheader();w.writerows(results)
with (OUT/'sample_transitions.csv').open('w',newline='',encoding='utf-8-sig') as f:
    w=csv.DictWriter(f,fieldnames=list(transitions[0]));w.writeheader();w.writerows(transitions)
(OUT/'final_statistics.json').write_text(json.dumps({'protocol':{'development_set':'DCASE17-T4','test_sets':5,'frozen_alpha':.3,'frozen_Nr':5,'bootstrap_repetitions':10000,'bootstrap_seed_base':2026,'McNemar':'exact two-sided','correction':'Holm over five tests'},'results':results},ensure_ascii=False,indent=2),encoding='utf-8')
lines=['# Task 24 final paired statistics','','Frozen on DCASE: `alpha=.3, Nr=5`. DCASE is excluded from inference.','','| Dataset | dHit@1 [95% CI] | rescued/harmed | McNemar p | Holm p | dMRR [95% CI] |','|---|---:|---:|---:|---:|---:|']
for x in results:lines.append(f"| {x['dataset']} | {x['delta_Hit@1_pp']:+.3f} [{x['Hit@1_CI95_low']:+.3f}, {x['Hit@1_CI95_high']:+.3f}] | {x['wrong_to_correct']}/{x['correct_to_wrong']} | {x['McNemar_exact_p']:.4g} | {x['McNemar_Holm_p_5']:.4g} | {x['delta_MRR_pp']:+.3f} [{x['MRR_CI95_low']:+.3f}, {x['MRR_CI95_high']:+.3f}] |")
(OUT/'REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
