#!/usr/bin/env python3
"""Task23C: expanded DCASE validation grid with Hit@1-first selection."""
import csv
import importlib.util
import json
from pathlib import Path

ROOT=Path('/data/zkx/zkx/review1')
OUT=ROOT/'23C_DCASE_validation_expanded_Nr'
spec=importlib.util.spec_from_file_location('task23_core',str(ROOT/'task23_dcase_validation.py'))
core=importlib.util.module_from_spec(spec);spec.loader.exec_module(core)
core.OUT=OUT
core.N_RELATIONS=(1,3,5,10,47)
core.METHODS=[f'TFS_alpha{a:.1f}_Nr{nr}' for nr in core.N_RELATIONS for a in core.ALPHAS]
core.main()

# Formal selection: Nr=47 is an all-relations control and is not eligible.
metrics=json.loads((OUT/'metrics.json').read_text(encoding='utf-8'))
eligible=[m for m in core.METHODS if not m.endswith('_Nr47')]
best_hit=max(metrics[m]['Hit@1'] for m in eligible)
hit_ties=[m for m in eligible if metrics[m]['Hit@1']==best_hit]
best_mrr=max(metrics[m]['MRR'] for m in hit_ties)
mrr_ties=[m for m in hit_ties if metrics[m]['MRR']==best_mrr]
selected=min(mrr_ties,key=lambda m:int(m.rsplit('Nr',1)[1]))
decision={'primary_metric':'Hit@1','secondary_metric':'MRR','eligible_Nr':[1,3,5,10],
          'Nr47_role':'all-relations/no-selection control only','best_Hit@1':best_hit,
          'Hit@1_tied_configs':hit_ties,'best_MRR_within_Hit@1_ties':best_mrr,
          'selected':selected,'selection_rule':'maximize Hit@1; exact ties maximize MRR; remaining ties prefer smaller Nr'}
(OUT/'selected_config_hit1_first.json').write_text(json.dumps(decision,ensure_ascii=False,indent=2),encoding='utf-8')

rows=list(csv.DictReader((OUT/'validation_grid.csv').open(encoding='utf-8-sig')))
for row in rows:
    row['selected']=str(row['method']==selected).lower()
    row['role']='all-relations control' if row['method'].endswith('_Nr47') else 'eligible validation configuration'
with (OUT/'validation_grid_hit1_first.csv').open('w',newline='',encoding='utf-8-sig') as f:
    fields=list(rows[0]);w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
print(json.dumps(decision,indent=2))
