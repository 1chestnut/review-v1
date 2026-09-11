#!/usr/bin/env python3
import csv, hashlib, json
from pathlib import Path
import numpy as np
from scipy.stats import binomtest

ROOT=Path('/data/zkx/zkx/review1/26_relation_selection_AAKV_control')
SETS=[('01_ESC50','ESC-50'),('02_UrbanSound8K','UrbanSound8K'),('03_FSD50K','FSD50K'),('05_AudioSet','AudioSet'),('06_TUT2017','TUT2017')]
RANDOM=['AAKV-Random5-s42','AAKV-Random5-s43','AAKV-Random5-s44']

def stats(a,b,seed,reps=10000):
 a=np.asarray(a,float);b=np.asarray(b,float);ac=a==1;bc=b==1
 rescue=int(np.sum(~ac&bc));harm=int(np.sum(ac&~bc));n=rescue+harm
 p=float(binomtest(min(rescue,harm),n,.5).pvalue) if n else 1.
 dh=bc.astype(float)-ac.astype(float);dr=1/b-1/a;rng=np.random.default_rng(seed);hs=[];rs=[]
 for start in range(0,reps,250):
  idx=rng.integers(0,len(a),size=(min(250,reps-start),len(a)));hs.append(dh[idx].mean(1)*100);rs.append(dr[idx].mean(1)*100)
 h=np.concatenate(hs);r=np.concatenate(rs)
 return {'delta_Hit@1_pp':100*dh.mean(),'Hit@1_CI_low':np.percentile(h,2.5),'Hit@1_CI_high':np.percentile(h,97.5),
         'rescued':rescue,'harmed':harm,'McNemar_p':p,'delta_MRR_pp':100*dr.mean(),'MRR_CI_low':np.percentile(r,2.5),'MRR_CI_high':np.percentile(r,97.5)}

main=[];paired=[]
for ds,name in SETS:
 met=json.loads((ROOT/ds/'metrics.json').read_text());rows=json.loads((ROOT/ds/'samples.json').read_text())
 for method,v in met.items():main.append({'dataset':name,'method':method,**v})
 rand={k:float(np.mean([met[m][k] for m in RANDOM])) for k in ['Hit@1','Hit@3','Hit@5','MRR']}
 rand.update({k+'_sd':float(np.std([met[m][k] for m in RANDOM],ddof=1)) for k in ['Hit@1','Hit@3','Hit@5','MRR']})
 main.append({'dataset':name,'method':'AAKV-Random5-mean',**rand})
 ranks={m:[x['ranks'][m] for x in rows] for m in met}
 # A fixed per-sample mean reciprocal-rank random reference for descriptive comparison only.
 for baseline in ['AAKV-FrozenRq','AAKV-Frequency5']+RANDOM:
  seed=260000+int(hashlib.sha256(f'{name}|{baseline}'.encode()).hexdigest()[:8],16)
  paired.append({'dataset':name,'comparison':f'AAKV-Selector5 vs {baseline}',**stats(ranks[baseline],ranks['AAKV-Selector5'],seed)})

def write(path,rows):
 keys=[]
 for x in rows:
  for k in x:
   if k not in keys:keys.append(k)
 with path.open('w',newline='',encoding='utf-8-sig') as f:
  w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(rows)
write(ROOT/'01_all_metrics.csv',main);write(ROOT/'02_paired_statistics.csv',paired)
lines=['# Task26 relation-selection results','',
'All branches use the same AAKV text and frozen Fusion; only relation selection changes.','',
'| Dataset | FrozenRq H1/MRR | Frequency5 H1/MRR | Random5 mean H1/MRR | Selector5 H1/MRR | Δ Selector−Frozen H1/MRR |',
'|---|---:|---:|---:|---:|---:|']
for ds,name in SETS:
 d={x['method']:x for x in main if x['dataset']==name};s=d['AAKV-Selector5'];f=d['AAKV-FrozenRq'];q=d['AAKV-Frequency5'];r=d['AAKV-Random5-mean']
 lines.append(f"| {name} | {f['Hit@1']:.3f}/{f['MRR']:.3f} | {q['Hit@1']:.3f}/{q['MRR']:.3f} | {r['Hit@1']:.3f}/{r['MRR']:.3f} | {s['Hit@1']:.3f}/{s['MRR']:.3f} | {s['Hit@1']-f['Hit@1']:+.3f}/{s['MRR']-f['MRR']:+.3f} |")
lines+=['','## Paired Selector5 versus FrozenRq','', '| Dataset | ΔHit@1 [95% CI] | rescued/harmed | McNemar p | ΔMRR [95% CI] |','|---|---:|---:|---:|---:|']
for x in paired:
 if not x['comparison'].endswith('AAKV-FrozenRq'):continue
 lines.append(f"| {x['dataset']} | {x['delta_Hit@1_pp']:+.3f} [{x['Hit@1_CI_low']:+.3f},{x['Hit@1_CI_high']:+.3f}] | {x['rescued']}/{x['harmed']} | {x['McNemar_p']:.4g} | {x['delta_MRR_pp']:+.3f} [{x['MRR_CI_low']:+.3f},{x['MRR_CI_high']:+.3f}] |")
(ROOT/'REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
(ROOT/'summary_complete.json').write_text(json.dumps({'completed':True,'datasets':[n for _,n in SETS]},indent=2),encoding='utf-8')
print((ROOT/'REPORT.md').read_text())
