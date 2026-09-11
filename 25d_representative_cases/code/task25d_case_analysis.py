#!/usr/bin/env python3
"""Task25(d): post-hoc representative cases from frozen per-sample Task25 outputs."""
import csv, importlib.util, json
from pathlib import Path
import numpy as np
import torch

ROOT=Path('/data/zkx/zkx/review1');SRC=ROOT/'25_final_experiment_alpha03_Nr5'/'test';OUT=ROOT/'25d_representative_cases'
AAKV=ROOT/'20A_topP5_aligned_selector_exploration/aakv_all.json'
DATASETS=[('01_ESC50','ESC-50'),('02_UrbanSound8K','UrbanSound8K'),('03_FSD50K','FSD50K'),('05_AudioSet','AudioSet'),('06_TUT2017','TUT2017')]
METHODS=['CLAP','I_iKnow','T_AAKV','F_Fusion','S_Selector','TF','TS','FS','TFS_Final']

def load_module(path,name):
 s=importlib.util.spec_from_file_location(name,str(path));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def label_list(ds):
 rt=load_module(ROOT/'12_shared-abcd-statistics'/ds/'frozen_inputs'/'runtime.py','labels_'+ds);return list(rt.load_dataset()['label_classes'])

def texts_for(ds,classes,row,pred,true):
 cache=torch.load(ROOT/f'18a_relation_oracle_audit/{ds}/results/static_relation_cache.pt',map_location='cpu');aakv=json.loads(AAKV.read_text(encoding='utf-8'))['texts']
 rels=row['selected']['TFS_Final']['relations'];result={}
 for role,ci in [('final_prediction',pred),('ground_truth_reference',true)]:
  items=[]
  for rel in rels:
   tails=cache['tails'][rel].get(ci,[])
   if tails:
    tail,prompt=tails[0];key='\t'.join((prompt.split(', ',1)[0],rel,tail));items.append({'relation':rel,'tail':tail,'direct_triple':prompt,'AAKV_text':aakv.get(key),'choice':'Top-1 KGE tail within this selected relation'})
  result[role]={'class':classes[ci],'evidence':items}
 return result

def choose(records,n=3):
 records=sorted(records,key=lambda x:(-x['priority'],x['dataset'],x['sample_index']));picked=[];used=set()
 for x in records:
  if x['dataset'] not in used:picked.append(x);used.add(x['dataset'])
  if len(picked)==n:return picked
 for x in records:
  if x not in picked:picked.append(x)
  if len(picked)==n:return picked
 return picked

def main():
 OUT.mkdir(parents=True,exist_ok=True);groups={k:[] for k in ['AAKV_only_rescue','Selector_only_rescue','TFS_combination_only_rescue','TFS_harm']};counts=[]
 raw={}
 for ds,name in DATASETS:
  rows=json.loads((SRC/ds/'samples.json').read_text(encoding='utf-8'));npz=np.load(SRC/ds/'predictions.npz');scores=npz['scores'];stored=[str(x) for x in npz['methods']]
  if stored!=METHODS:raise RuntimeError(f'{name}: unexpected method order {stored}')
  classes=label_list(ds);local={k:0 for k in groups}
  for i,row in enumerate(rows):
   ok={m:row['ranks'][m]==1 for m in METHODS};kind=None
   if ok['T_AAKV'] and not any(ok[m] for m in ['I_iKnow','F_Fusion','S_Selector']):kind='AAKV_only_rescue'
   if ok['S_Selector'] and not any(ok[m] for m in ['I_iKnow','T_AAKV','F_Fusion']):kind='Selector_only_rescue'
   if ok['TFS_Final'] and not any(ok[m] for m in ['I_iKnow','T_AAKV','F_Fusion','S_Selector','TF','TS','FS']):kind='TFS_combination_only_rescue'
   if ok['I_iKnow'] and not ok['TFS_Final']:kind='TFS_harm'
   if kind:
    preds={m:int(np.argmax(scores[i,j])) for j,m in enumerate(METHODS)};truth=int(row['true_indices'][0]);priority=(1/row['ranks']['TFS_Final']-1/row['ranks']['I_iKnow']) if kind!='TFS_harm' else (1/row['ranks']['I_iKnow']-1/row['ranks']['TFS_Final'])
    rec={'case_type':kind,'dataset':name,'dataset_id':ds,'sample_index':row['sample_index'],'audio_path':row['audio_path'],'truth_indices':row['true_indices'],'truth_labels':[classes[int(x)] for x in row['true_indices']],
      'CLAP_prediction':classes[preds['CLAP']],'iKnow_prediction':classes[preds['I_iKnow']],'module_prediction':classes[preds['T_AAKV'] if kind=='AAKV_only_rescue' else preds['S_Selector'] if kind=='Selector_only_rescue' else preds['TFS_Final']],
      'TFS_prediction':classes[preds['TFS_Final']],'selected_relations':row['selected']['TFS_Final']['relations'],'ranks':row['ranks'],'priority':float(priority),'pred_indices':preds}
    groups[kind].append(rec);local[kind]+=1;raw[(ds,row['sample_index'])]=(row,classes,preds,truth)
  counts.append({'dataset':name,**local})
 selected=[]
 for kind,records in groups.items():selected.extend(choose(records,3))
 detailed=[]
 for rec in selected:
  row,classes,preds,truth=raw[(rec['dataset_id'],rec['sample_index'])];x=dict(rec);x['evidence_details']=texts_for(rec['dataset_id'],classes,row,preds['TFS_Final'],truth);detailed.append(x)
 with (OUT/'01_candidate_counts.csv').open('w',newline='',encoding='utf-8-sig') as f:w=csv.DictWriter(f,fieldnames=list(counts[0]));w.writeheader();w.writerows(counts)
 flat=[]
 for x in detailed:flat.append({k:(json.dumps(v,ensure_ascii=False) if isinstance(v,(list,dict)) else v) for k,v in x.items() if k not in ('priority','pred_indices','dataset_id')})
 with (OUT/'02_representative_cases.csv').open('w',newline='',encoding='utf-8-sig') as f:w=csv.DictWriter(f,fieldnames=list(flat[0]));w.writeheader();w.writerows(flat)
 (OUT/'03_representative_cases.json').write_text(json.dumps(detailed,ensure_ascii=False,indent=2),encoding='utf-8')
 protocol={'analysis':'post-hoc only','source':'Task25 frozen per-sample ranks and scores','ground_truth_use':'only categorization after inference; never method routing','strict_definitions':{
  'AAKV_only_rescue':'T correct while iKnow, F-only and S-only are wrong','Selector_only_rescue':'S correct while iKnow, T-only and F-only are wrong','TFS_combination_only_rescue':'TFS correct while all seven incomplete branches are wrong','TFS_harm':'iKnow correct but TFS wrong'},
  'representative_selection':'largest reciprocal-rank improvement (or damage), prefer distinct datasets; maximum three per category','evidence_display':'Top-1 KGE-ranked tail per TFS-selected relation for final-predicted and first ground-truth class; it is not relabeled as the highest audio-similarity evidence'}
 (OUT/'protocol.json').write_text(json.dumps(protocol,ensure_ascii=False,indent=2),encoding='utf-8')
 lines=['# Task25(d) representative case analysis','','Cases are selected strictly after inference. Ground truth is never used by the method.','','| Type | Dataset | Truth | CLAP | iKnow | TFS | Selected relations |','|---|---|---|---|---|---|---|']
 for x in detailed:lines.append(f"| {x['case_type']} | {x['dataset']} | {', '.join(x['truth_labels'])} | {x['CLAP_prediction']} | {x['iKnow_prediction']} | {x['TFS_prediction']} | {', '.join(x['selected_relations'])} |")
 (OUT/'REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8');(OUT/'progress.json').write_text(json.dumps({'completed':True,'selected_cases':len(detailed)},indent=2))

if __name__=='__main__':main()
