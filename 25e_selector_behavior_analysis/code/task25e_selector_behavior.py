#!/usr/bin/env python3
"""Task25(e): post-hoc, label-free-selector behavior audit from Task25 outputs."""
import ast,csv,json,math
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
import torch

ROOT=Path('/data/zkx/zkx/review1');SRC=ROOT/'25_final_experiment_alpha03_Nr5'/'test';OUT=ROOT/'25e_selector_behavior_analysis'
DATASETS=[('01_ESC50','ESC-50'),('02_UrbanSound8K','UrbanSound8K'),('03_FSD50K','FSD50K'),('05_AudioSet','AudioSet'),('06_TUT2017','TUT2017')]

def write_csv(path,rows):
 with path.open('w',newline='',encoding='utf-8-sig') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def frozen_relations(ds):
 tree=ast.parse((ROOT/'12_shared-abcd-statistics'/ds/'frozen_inputs'/'runtime.py').read_text(encoding='utf-8'))
 for node in tree.body:
  if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='HOP1_RELATIONS' for t in node.targets):return ast.literal_eval(node.value)
 raise RuntimeError(f'{ds}: HOP1_RELATIONS not found')

def entropy(counts):
 x=np.asarray(list(counts.values()),float);p=x/x.sum();return float(-(p*np.log(p)).sum())

def metrics(rows,a,b):
 ra=np.asarray([x['ranks'][a] for x in rows],float);rb=np.asarray([x['ranks'][b] for x in rows],float)
 ah=ra==1;bh=rb==1
 return {'iKnow_Hit1':100*ah.mean(),'TFS_Hit1':100*bh.mean(),'delta_Hit1_pp':100*(bh.astype(float)-ah.astype(float)).mean(),'iKnow_MRR':100*np.mean(1/ra),'TFS_MRR':100*np.mean(1/rb),'delta_MRR_pp':100*np.mean(1/rb-1/ra),'wrong_to_correct':int(np.sum(~ah&bh)),'correct_to_wrong':int(np.sum(ah&~bh)),'net_rescued':int(np.sum(~ah&bh)-np.sum(ah&~bh))}

def main():
 OUT.mkdir(parents=True,exist_ok=True);summaries=[];freq_rows=[];vote_rows=[];effect_rows=[];class_rows=[]
 for ds,name in DATASETS:
  rows=json.loads((SRC/ds/'samples.json').read_text(encoding='utf-8'));cache=torch.load(ROOT/f'18a_relation_oracle_audit/{ds}/results/static_relation_cache.pt',map_location='cpu');pool=list(cache['relations']);frozen=set(frozen_relations(ds))
  top=Counter();included=Counter();sets=Counter();votes=Counter();outside=[];overlaps=[];by_vote=defaultdict(list);by_rel=defaultdict(list);by_class=defaultdict(list)
  for x in rows:
   meta=x['selected']['TFS_Final'];rels=list(meta['relations']);sig=tuple(sorted(rels));sets[sig]+=1;top[rels[0]]+=1;included.update(rels);votes[int(meta['votes'])]+=1
   outside.append(sum(r not in frozen for r in rels)/len(rels));overlaps.append(len(set(rels)&frozen)/len(set(rels)|frozen))
   by_vote[int(meta['votes'])].append(x)
   for r in rels:by_rel[r].append(x)
   for c in x['true_indices']:by_class[int(c)].append(rels)
  n=len(rows);h=entropy(top);hn=h/math.log(len(pool)) if len(pool)>1 else 0.;dominant_set,count=sets.most_common(1)[0]
  summaries.append({'dataset':name,'n_samples':n,'candidate_relations':len(pool),'retained_relations_per_sample':len(next(iter(sets))[0]),'unique_relations_ever_selected':len(included),'unique_unordered_relation_sets':len(sets),'dominant_set_share_percent':100*count/n,'top1_relation_entropy':h,'normalized_top1_relation_entropy':hn,'mean_fraction_selected_outside_frozen_iKnow_set':float(np.mean(outside)),'mean_Jaccard_with_frozen_iKnow_set':float(np.mean(overlaps)),'fraction_samples_exactly_equal_frozen_set':100*sum(set(sig)==frozen for sig,c in sets.items() for _ in range(c))/n})
  for r in pool:
   freq_rows.append({'dataset':name,'relation':r,'top1_count':top[r],'top1_percent':100*top[r]/n,'included_count':included[r],'included_percent':100*included[r]/n,'in_frozen_iKnow_relation_set':r in frozen})
   if by_rel[r]:effect_rows.append({'dataset':name,'relation':r,'selected_samples':len(by_rel[r]),**metrics(by_rel[r],'I_iKnow','TFS_Final'),'warning':'descriptive conditional subset; relations co-occur and this is not a causal effect'})
  for v,group in sorted(by_vote.items()):vote_rows.append({'dataset':name,'consensus_votes':v,'vote_fraction_of_pool':v/len(pool),'n_samples':len(group),**metrics(group,'I_iKnow','TFS_Final')})
  for c,rel_lists in sorted(by_class.items()):
   ct=Counter(r for rels in rel_lists for r in rels);tops=Counter(rels[0] for rels in rel_lists)
   class_rows.append({'dataset':name,'true_class_index':c,'n_label_occurrences':len(rel_lists),'unique_relations_selected':len(ct),'unique_top1_relations':len(tops),'dominant_top1_relation':tops.most_common(1)[0][0],'dominant_top1_share_percent':100*tops.most_common(1)[0][1]/len(rel_lists),'normalized_top1_entropy':entropy(tops)/math.log(len(pool)) if len(tops)>1 else 0.})
 write_csv(OUT/'01_dataset_selector_summary.csv',summaries);write_csv(OUT/'02_relation_frequency.csv',freq_rows);write_csv(OUT/'03_performance_by_consensus_votes.csv',vote_rows);write_csv(OUT/'04_descriptive_effect_when_relation_selected.csv',effect_rows);write_csv(OUT/'05_within_class_relation_diversity.csv',class_rows)
 protocol={'source':'Task25 frozen TFS_Final sample records','analysis_type':'post-hoc descriptive mechanism audit','reruns_model':False,'uses_labels_for_selector':False,'ground_truth_use':'only retrospective correctness and within-class summaries','does_not_select_parameters':True,'definitions':{'top1_relation':'first relation in the frozen Consensus-Margin ordering','consensus_votes':'number of candidate relation experts predicting the consensus class','normalized_entropy':'entropy of top-1 relation distribution divided by log(candidate relation count)','dominant_set_share':'largest frequency of an unordered selected-Nr relation set','Jaccard':'selected relation set versus frozen iKnow dataset relation set'},'caution':'Relation-conditioned effects are descriptive because five selected relations co-occur; they must not be interpreted causally.'}
 (OUT/'protocol.json').write_text(json.dumps(protocol,ensure_ascii=False,indent=2),encoding='utf-8')
 lines=['# Task25(e) Selector behavior analysis','','This is a post-hoc explanation of the frozen Task25 selector. No result is used to modify the method or parameters.','','| Dataset | unique used / pool | unique selected sets | dominant set share | normalized top-1 entropy | outside frozen set | mean Jaccard |','|---|---:|---:|---:|---:|---:|---:|']
 for x in summaries:lines.append(f"| {x['dataset']} | {x['unique_relations_ever_selected']}/{x['candidate_relations']} | {x['unique_unordered_relation_sets']} | {x['dominant_set_share_percent']:.2f}% | {x['normalized_top1_relation_entropy']:.3f} | {100*x['mean_fraction_selected_outside_frozen_iKnow_set']:.2f}% | {x['mean_Jaccard_with_frozen_iKnow_set']:.3f} |")
 lines += ['','Interpretation rules: low dominant-set share and non-zero entropy indicate sample-dependent behavior; they do not by themselves prove better accuracy. Performance-by-vote tables show association, not causation.']
 (OUT/'REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8');(OUT/'progress.json').write_text(json.dumps({'completed':True,'datasets':len(DATASETS)},indent=2))

if __name__=='__main__':main()
