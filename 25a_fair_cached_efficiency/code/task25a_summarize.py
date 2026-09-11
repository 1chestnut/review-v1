#!/usr/bin/env python3
import csv,json
from pathlib import Path
R=Path('/data/zkx/zkx/review1/25a_fair_cached_efficiency');D=['01_ESC50','02_UrbanSound8K','03_FSD50K','05_AudioSet','06_TUT2017'];names={'01_ESC50':'ESC-50','02_UrbanSound8K':'UrbanSound8K','03_FSD50K':'FSD50K','05_AudioSet':'AudioSet','06_TUT2017':'TUT2017'}
rows=[]
for d in D:
 for x in csv.DictReader((R/d/'timing_summary.csv').open(encoding='utf-8-sig')):x['dataset']=names[d];rows.append(x)
with (R/'01_efficiency_complete.csv').open('w',newline='',encoding='utf-8-sig') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
# Pair runtime with Task25 full-data accuracy, never with the timing subset.
trade=[]
for d in D:
 met={x['method']:x for x in csv.DictReader((Path('/data/zkx/zkx/review1/25_final_experiment_alpha03_Nr5/test')/d/'metrics.csv').open())}
 tim=[x for x in rows if x['dataset']==names[d] and x['batch_size']=='1'];tm={x['method']:x for x in tim}
 for method,m25 in [('Frozen-iKnow','I_iKnow'),('Final-TFS','TFS_Final')]:
  b=met['I_iKnow'];v=met[m25];extra=float(tm[method]['end_to_end_ms_per_sample_mean'])-float(tm['Frozen-iKnow']['end_to_end_ms_per_sample_mean'])
  dm=float(v['MRR'])-float(b['MRR']);trade.append({'dataset':names[d],'method':method,'Hit@1':v['Hit@1'],'MRR':v['MRR'],'delta_Hit@1_vs_iKnow_pp':float(v['Hit@1'])-float(b['Hit@1']),'delta_MRR_vs_iKnow_pp':dm,'extra_e2e_ms_vs_iKnow':extra,'delta_MRR_pp_per_extra_ms':dm/extra if extra>0 else ''})
with (R/'02_performance_efficiency_tradeoff.csv').open('w',newline='',encoding='utf-8-sig') as f:w=csv.DictWriter(f,fieldnames=list(trade[0]));w.writeheader();w.writerows(trade)
(R/'summary_complete.json').write_text(json.dumps({'completed':True,'datasets':[names[d] for d in D]},indent=2))
