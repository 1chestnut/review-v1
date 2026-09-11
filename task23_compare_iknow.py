#!/usr/bin/env python3
"""Add Task21 CLAP/frozen-iKnow controls and deltas to Task23/23B grids."""
import csv
from pathlib import Path

ROOT = Path('/data/zkx/zkx/review1')
T21 = ROOT/'21_noTopP_factorial_vs_frozen_iKnow'
TARGETS = {
    '04_DCASE17_T4': ROOT/'23_DCASE_validation_alpha_Nr',
    '01_ESC50': ROOT/'23B_five_test_parameter_diagnostic/01_ESC50',
    '02_UrbanSound8K': ROOT/'23B_five_test_parameter_diagnostic/02_UrbanSound8K',
    '03_FSD50K': ROOT/'23B_five_test_parameter_diagnostic/03_FSD50K',
    '05_AudioSet': ROOT/'23B_five_test_parameter_diagnostic/05_AudioSet',
    '06_TUT2017': ROOT/'23B_five_test_parameter_diagnostic/06_TUT2017',
}

summary=[]
for dataset,out in TARGETS.items():
    controls={r['method']:r for r in csv.DictReader((T21/dataset/'metrics.csv').open(encoding='utf-8-sig'))}
    clap=controls['CLAP']; iknow=controls['I_Frozen-iKnow-05b']
    grid=list(csv.DictReader((out/'validation_grid.csv').open(encoding='utf-8-sig')))
    fields=['method','alpha','Nr','Hit@1','Hit@3','Hit@5','MRR','delta_Hit@1_vs_iKnow','delta_MRR_vs_iKnow','selected']
    rows=[]
    for name,control in [('CLAP',clap),('I_Frozen-iKnow-05b',iknow)]:
        rows.append({'method':name,'alpha':'','Nr':'','Hit@1':control['Hit@1'],'Hit@3':control['Hit@3'],
                     'Hit@5':control['Hit@5'],'MRR':control['MRR'],
                     'delta_Hit@1_vs_iKnow':float(control['Hit@1'])-float(iknow['Hit@1']),
                     'delta_MRR_vs_iKnow':float(control['MRR'])-float(iknow['MRR']),'selected':'false'})
    for row in grid:
        row['delta_Hit@1_vs_iKnow']=float(row['Hit@1'])-float(iknow['Hit@1'])
        row['delta_MRR_vs_iKnow']=float(row['MRR'])-float(iknow['MRR'])
        rows.append(row)
    with (out/'validation_grid_vs_iKnow.csv').open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
    chosen=next(r for r in grid if r['method']=='TFS_alpha0.7_Nr3')
    numerical_best=max(grid,key=lambda r:float(r['MRR']))
    summary.append({'dataset':dataset,'iKnow_Hit@1':iknow['Hit@1'],'iKnow_MRR':iknow['MRR'],
        'DCASE_selected_Hit@1':chosen['Hit@1'],'DCASE_selected_MRR':chosen['MRR'],
        'delta_Hit@1_vs_iKnow':float(chosen['Hit@1'])-float(iknow['Hit@1']),
        'delta_MRR_vs_iKnow':float(chosen['MRR'])-float(iknow['MRR']),
        'posthoc_best_config':numerical_best['method'],'posthoc_best_MRR':numerical_best['MRR'],
        'MRR_gap_to_posthoc_best':float(numerical_best['MRR'])-float(chosen['MRR'])})

with (ROOT/'23B_five_test_parameter_diagnostic'/'DCASE_SELECTED_TRANSFER_VS_IKNOW.csv').open('w',newline='',encoding='utf-8-sig') as f:
    w=csv.DictWriter(f,fieldnames=list(summary[0]));w.writeheader();w.writerows(summary)
