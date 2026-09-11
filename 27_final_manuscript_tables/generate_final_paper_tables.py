#!/usr/bin/env python3
import csv,json
from pathlib import Path
import numpy as np

ROOT=Path('/data/zkx/zkx/review1');OUT=ROOT/'27_final_manuscript_tables';OUT.mkdir(parents=True,exist_ok=True)
T25=ROOT/'25_final_experiment_alpha03_Nr5';T11=ROOT/'11_iknow-formula-text-contribution';T25G=ROOT/'25g_RawTriple_FS_control';T26=ROOT/'26_relation_selection_AAKV_control'
SETS=[('01_ESC50','ESC-50'),('02_UrbanSound8K','UrbanSound8K'),('03_FSD50K','FSD50K'),('05_AudioSet','AudioSet'),('06_TUT2017','TUT2017')]
MET=['Hit@1','Hit@3','Hit@5','MRR']

def readcsv(p):
 with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def write(p,rows):
 keys=[]
 for x in rows:
  for k in x:
   if k not in keys:keys.append(k)
 with p.open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(rows)
def f(x):return float(x)

# Table 1: final main results.
main=readcsv(T25/'01_final_main_results.csv');write(OUT/'Table1_main_results.csv',main)

# Table 2: complete factorial ablation, long form plus macro mean.
abl=[]
for ds,name in SETS:
 m=json.loads((T25/'test'/ds/'metrics.json').read_text())
 for method in ['I_iKnow','T_AAKV','F_Fusion','S_Selector','TF','TS','FS','TFS_Final']:
  abl.append({'dataset':name,'method':method,**m[method]})
for method in ['I_iKnow','T_AAKV','F_Fusion','S_Selector','TF','TS','FS','TFS_Final']:
 rows=[x for x in abl if x['method']==method]
 abl.append({'dataset':'MacroMean','method':method,**{k:float(np.mean([x[k] for x in rows])) for k in MET}})
write(OUT/'Table2_factorial_ablation.csv',abl)

# Table 3: AAKV verbalization, explicitly separated by experimental context.
aakv=[]
for ds,name in SETS:
 rows={x['method']:x for x in readcsv(T11/ds/'results/iknow_formula_text_ablation.csv')}
 for method in ['iKnow-05-Direct','RawTriple','Qwen-General','AAKV']:
  aakv.append({'panel':'A: fixed iKnow aggregation and FrozenRq','dataset':name,'method':method,**{k:f(rows[method][k]) for k in MET}})
 m25=json.loads((T25/'test'/ds/'metrics.json').read_text());raw=json.loads((T25G/ds/'metrics.json').read_text())['Raw-FS']
 for method,vals in [('Direct-FS',m25['FS']),('Raw-FS',raw),('AAKV-TFS',m25['TFS_Final'])]:
  aakv.append({'panel':'B: frozen Fusion+Selector system','dataset':name,'method':method,**vals})
write(OUT/'Table3_AAKV_verbalization.csv',aakv)

# Table 4: relation-selection controls.
selector=[]
randoms=['AAKV-Random5-s42','AAKV-Random5-s43','AAKV-Random5-s44']
for ds,name in SETS:
 m=json.loads((T26/ds/'metrics.json').read_text())
 for method in ['AAKV-FrozenRq','AAKV-Frequency5']:
  selector.append({'dataset':name,'method':method,**m[method]})
 selector.append({'dataset':name,'method':'AAKV-Random5-mean',**{k:float(np.mean([m[r][k] for r in randoms])) for k in MET},**{k+'_SD':float(np.std([m[r][k] for r in randoms],ddof=1)) for k in MET}})
 selector.append({'dataset':name,'method':'AAKV-Selector5',**m['AAKV-Selector5']})
write(OUT/'Table4_relation_selector.csv',selector)

# Table 5: frozen protocol and parameter provenance.
params=[
 {'parameter':'Development dataset','value':'DCASE17-T4, 419 available samples','meaning':'Select method-level hyperparameters only','selection/provenance':'Declared development set; excluded from the five final test datasets','test_status':'not reported as test result'},
 {'parameter':'K','value':'5','meaning':'CLAP top candidate classes receiving KG enrichment','selection/provenance':'Inherited and frozen from the iKnow reproduction','test_status':'fixed'},
 {'parameter':'M','value':'3','meaning':'RotatE tail entities retained per (head, relation)','selection/provenance':'Inherited and frozen from the iKnow reproduction','test_status':'fixed'},
 {'parameter':'kappa','value':'100','meaning':'Normalized log-sum-exp similarity scale','selection/provenance':'Aligned with the frozen CLAP/iKnow reproduction score scale','test_status':'fixed'},
 {'parameter':'alpha','value':'0.3','meaning':'Base CLAP weight; knowledge weight is 1-alpha','selection/provenance':'Selected once on DCASE development set by MRR','test_status':'fixed on all five tests'},
 {'parameter':'N_r','value':'5','meaning':'Relations retained by the sample-level selector','selection/provenance':'Selected jointly with alpha on DCASE development set','test_status':'fixed on all five tests'},
 {'parameter':'Candidate relation pool','value':'47 RotatE relations','meaning':'Relations available to the selector','selection/provenance':'Complete frozen KG relation vocabulary; not selected using test labels','test_status':'fixed'},
 {'parameter':'Top-P','value':'All (disabled)','meaning':'No additional evidence-score pruning','selection/provenance':'Removed after controlled analysis showed no necessary contribution','test_status':'fixed'},
 {'parameter':'Hop','value':'1','meaning':'One-hop KG enrichment','selection/provenance':'Second-hop branch removed from the final method','test_status':'fixed'},
 {'parameter':'Knowledge text','value':'AAKV','meaning':'Constrained audio-aware KG verbalization','selection/provenance':'Generated offline with fixed prompt, verification and recorded fallback protocol','test_status':'frozen before inference'},
 {'parameter':'Seed','value':'42 + SHA256(audio path)','meaning':'Deterministic per-sample execution','selection/provenance':'Same sample seed for every compared branch','test_status':'fixed'},
 {'parameter':'Primary metrics','value':'Hit@1, Hit@3, Hit@5, MRR','meaning':'Ranking evaluation; highest-ranked positive used for multi-label samples','selection/provenance':'One common evaluator for all methods','test_status':'fixed'},
]
write(OUT/'Table5_parameters_and_protocol.csv',params)

# Readable manuscript-oriented Markdown.
def cell(v):return f"{float(v):.2f}"
lines=['# Final manuscript experiment tables','',
'All reported final-test values use the five test datasets. DCASE17-T4 is used only for development and parameter selection.','',
'## Table 1. Main results (%)','',
'| Dataset | Method | Hit@1 | Hit@3 | Hit@5 | MRR |','|---|---|---:|---:|---:|---:|']
for x in main:lines.append(f"| {x['dataset']} | {x['method']} | {cell(x['Hit@1'])} | {cell(x['Hit@3'])} | {cell(x['Hit@5'])} | {cell(x['MRR'])} |")
lines+=['','## Table 2. Factorial ablation (Hit@1 / MRR, %)','',
'| Dataset | iKnow | AAKV | Fusion | Selector | AAKV+Fusion | AAKV+Selector | Fusion+Selector | Full |','|---|---:|---:|---:|---:|---:|---:|---:|---:|']
for name in [x[1] for x in SETS]+['MacroMean']:
 d={x['method']:x for x in abl if x['dataset']==name};ms=['I_iKnow','T_AAKV','F_Fusion','S_Selector','TF','TS','FS','TFS_Final']
 lines.append('| '+name+' | '+' | '.join(f"{d[m]['Hit@1']:.2f}/{d[m]['MRR']:.2f}" for m in ms)+' |')
lines+=['','## Table 3. AAKV verbalization analysis (Hit@1 / MRR, %)','',
'### Panel A. Fixed iKnow aggregation and fixed relations','',
'| Dataset | Direct | RawTriple | General LLM | AAKV |','|---|---:|---:|---:|---:|']
for _,name in SETS:
 d={x['method']:x for x in aakv if x['dataset']==name and x['panel'].startswith('A:')};ms=['iKnow-05-Direct','RawTriple','Qwen-General','AAKV']
 lines.append('| '+name+' | '+' | '.join(f"{d[m]['Hit@1']:.2f}/{d[m]['MRR']:.2f}" for m in ms)+' |')
lines+=['','### Panel B. Same Fusion+Selector system','',
'| Dataset | Direct-FS | Raw-FS | AAKV-TFS |','|---|---:|---:|---:|']
for _,name in SETS:
 d={x['method']:x for x in aakv if x['dataset']==name and x['panel'].startswith('B:')};ms=['Direct-FS','Raw-FS','AAKV-TFS']
 lines.append('| '+name+' | '+' | '.join(f"{d[m]['Hit@1']:.2f}/{d[m]['MRR']:.2f}" for m in ms)+' |')
lines+=['','## Table 4. Relation-selection comparison (Hit@1 / MRR, %)','',
'| Dataset | FrozenRq | Frequency5 | Random5 mean | Selector5 |','|---|---:|---:|---:|---:|']
for _,name in SETS:
 d={x['method']:x for x in selector if x['dataset']==name};ms=['AAKV-FrozenRq','AAKV-Frequency5','AAKV-Random5-mean','AAKV-Selector5']
 lines.append('| '+name+' | '+' | '.join(f"{d[m]['Hit@1']:.2f}/{d[m]['MRR']:.2f}" for m in ms)+' |')
lines+=['','## Table 5. Parameters and frozen protocol','',
'| Parameter | Value | Role | Source/selection | Test status |','|---|---|---|---|---|']
for x in params:lines.append(f"| {x['parameter']} | {x['value']} | {x['meaning']} | {x['selection/provenance']} | {x['test_status']} |")
(OUT/'FINAL_TABLES.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
provenance={'Table1':str(T25/'01_final_main_results.csv'),'Table2':str(T25/'test'),'Table3_panelA':str(T11),'Table3_panelB':[str(T25/'test'),str(T25G)],'Table4':str(T26),'Table5_validation':str(T25/'validation/DCASE_grid.csv'),'created_from_frozen_outputs':True}
(OUT/'PROVENANCE.json').write_text(json.dumps(provenance,indent=2),encoding='utf-8')
(OUT/'README.md').write_text('# Final paper tables\n\nFive manuscript tables generated directly from frozen experiment outputs. See `PROVENANCE.json` for sources. Values are not manually transcribed.\n',encoding='utf-8')
print(OUT/'FINAL_TABLES.md')
