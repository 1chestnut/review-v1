#!/usr/bin/env python3
import csv,json
from pathlib import Path
import numpy as np
R=Path('/data/zkx/zkx/review1/25_final_experiment_alpha03_Nr5');D=['01_ESC50','02_UrbanSound8K','03_FSD50K','05_AudioSet','06_TUT2017'];N=['ESC-50','UrbanSound8K','FSD50K','AudioSet','TUT2017']
M=['CLAP','I_iKnow','T_AAKV','F_Fusion','S_Selector','TF','TS','FS','TFS_Final'];Z={}
for d,n in zip(D,N):
 rows={x['method']:x for x in csv.DictReader((R/'test'/d/'metrics.csv').open())};Z[n]=rows
with (R/'01_final_main_results.csv').open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.writer(f);w.writerow(['dataset','method','Hit@1','Hit@3','Hit@5','MRR'])
 for n in N:
  for m in ['CLAP','I_iKnow','TFS_Final']:w.writerow([n,m]+[Z[n][m][k] for k in ['Hit@1','Hit@3','Hit@5','MRR']])
with (R/'02_ablation_hit1_mrr.csv').open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.writer(f);w.writerow(['method']+N+['MacroMean'])
 for m in M[1:]:
  cells=[f"{float(Z[n][m]['Hit@1']):.3f} / {float(Z[n][m]['MRR']):.3f}" for n in N]
  macro=f"{np.mean([float(Z[n][m]['Hit@1']) for n in N]):.3f} / {np.mean([float(Z[n][m]['MRR']) for n in N]):.3f}";w.writerow([m]+cells+[macro])
def val(n,m,k):return float(Z[n][m][k])
effects=[];inter=[]
for n in N:
 for k in ['Hit@1','MRR']:
  v={m:val(n,m,k) for m in M[1:]};I,T,F,S,TF,TS,FS,TFS=[v[x] for x in M[1:]]
  effects += [[n,k,'T',np.mean([T-I,TF-F,TS-S,TFS-FS])],[n,k,'F',np.mean([F-I,TF-T,FS-S,TFS-TS])],[n,k,'S',np.mean([S-I,TS-T,FS-F,TFS-TF])]]
  inter += [[n,k,'T:F',np.mean([TF-T-F+I,TFS-TS-FS+S])],[n,k,'T:S',np.mean([TS-T-S+I,TFS-TF-FS+F])],[n,k,'F:S',np.mean([FS-F-S+I,TFS-TF-TS+T])],[n,k,'T:F:S',TFS-TF-TS-FS+T+F+S-I]]
for path,data in [(R/'03_factorial_module_effects.csv',effects),(R/'04_module_interactions.csv',inter)]:
 with path.open('w',newline='',encoding='utf-8-sig') as f:w=csv.writer(f);w.writerow(['dataset','metric','effect','percentage_points']);w.writerows(data)
(R/'summary_complete.json').write_text(json.dumps({'completed':True,'datasets':N,'alpha':.3,'Nr':5},indent=2))
