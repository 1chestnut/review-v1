#!/usr/bin/env python3
"""Build a reviewable five-table experiment package under Task26."""
import json, shutil
from pathlib import Path

R=Path('/data/zkx/zkx/review1')
BASE=R/'26_relation_selection_AAKV_control'/'final_experiment_package'
SETS=['01_ESC50','02_UrbanSound8K','03_FSD50K','05_AudioSet','06_TUT2017']

def cp(src,dst):
 dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
def tree(src,dst,patterns=None):
 dst.mkdir(parents=True,exist_ok=True)
 for p in src.rglob('*'):
  if p.is_file() and (patterns is None or p.name in patterns):cp(p,dst/p.relative_to(src))
def write(path,text):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text,encoding='utf-8')
def code_with_local_runtime(src,dst):
 text=src.read_text(encoding='utf-8')
 # Keep frozen tensors/audio caches as declared data inputs, but import a packaged runtime copy.
 text=text.replace("runtime = load_module(source / \"frozen_inputs\" / \"runtime.py\")",
                   "runtime = load_module(Path(__file__).parent / 'runtime' / dataset / 'runtime.py')")
 text=text.replace("rt=mod(src/'frozen_inputs/runtime.py')",
                   "rt=mod(Path(__file__).parent/'runtime'/ds/'runtime.py')")
 write(dst,text)

folders={
 '01_main_table':'Final CLAP vs frozen iKnow vs complete AAKV+Fusion+Selector results.',
 '02_ablation_table':'Independent 2^3 factorial ablation of AAKV, Fusion and Selector.',
 '03_AAKV_table':'Text-verbalization controls in fixed-iKnow and complete-system contexts.',
 '04_Selector_table':'Frozen, frequency, random and sample-adaptive relation selection.',
 '05_parameter_table':'Development-set parameter selection and frozen test protocol.'}
for f in folders:
 (BASE/f/'code').mkdir(parents=True,exist_ok=True);(BASE/f/'results').mkdir(parents=True,exist_ok=True)

# Runtime code is copied into every computational table folder; runners do not import earlier task code.
for folder in ['01_main_table','02_ablation_table','03_AAKV_table','04_Selector_table']:
 for ds in SETS:
  cp(R/'12_shared-abcd-statistics'/ds/'frozen_inputs/runtime.py',BASE/folder/'code/runtime'/ds/'runtime.py')

# 01 Main table: exact final runner plus complete frozen outputs.
code_with_local_runtime(R/'25_final_experiment_alpha03_Nr5/code/task25_run.py',BASE/'01_main_table/code/run_main_experiment.py')
cp(R/'25_final_experiment_alpha03_Nr5/code/task25_summarize.py',BASE/'01_main_table/code/build_main_table.py')
cp(R/'25_final_experiment_alpha03_Nr5/01_final_main_results.csv',BASE/'01_main_table/results/Table1_main_results.csv')
for ds in SETS:tree(R/'25_final_experiment_alpha03_Nr5/test'/ds,BASE/'01_main_table/results/per_sample'/ds,{'metrics.json','metrics.csv','protocol.json','samples.json','predictions.npz','progress.json'})

# 02 Ablation: same single-pass independent-branch runner and paired statistics.
code_with_local_runtime(R/'25_final_experiment_alpha03_Nr5/code/task25_run.py',BASE/'02_ablation_table/code/run_factorial_ablation.py')
cp(R/'25c_task25_paired_statistics/code/task25c_statistics.py',BASE/'02_ablation_table/code/paired_statistics.py')
cp(R/'25h_consolidated_ablation/code/task25h_consolidated_ablation.py',BASE/'02_ablation_table/code/build_ablation_tables.py')
cp(R/'27_final_manuscript_tables/Table2_factorial_ablation.csv',BASE/'02_ablation_table/results/Table2_factorial_ablation.csv')
for name in ['01_complete_ablation_metrics.csv','02_module_effects_paired.csv','03_protocol_checks.csv','REPORT.md','summary_complete.json']:
 cp(R/'25h_consolidated_ablation'/name,BASE/'02_ablation_table/results'/name)

# 03 AAKV: fixed-iKnow runner + full-system runner + RawTriple control.
cp(R/'11_iknow-formula-text-contribution/run_iknow_text_ablation.py',BASE/'03_AAKV_table/code/run_fixed_iKnow_text_comparison.py')
code_with_local_runtime(R/'25_final_experiment_alpha03_Nr5/code/task25_run.py',BASE/'03_AAKV_table/code/run_full_AAKV_and_Direct.py')
code_with_local_runtime(R/'25g_RawTriple_FS_control/code/task25g_rawfs_control.py',BASE/'03_AAKV_table/code/run_full_RawTriple.py')
cp(R/'25g_RawTriple_FS_control/code/task25g_finalize.py',BASE/'03_AAKV_table/code/build_full_text_comparison.py')
cp(R/'27_final_manuscript_tables/Table3_AAKV_verbalization.csv',BASE/'03_AAKV_table/results/Table3_AAKV_verbalization.csv')
for ds in SETS:
 tree(R/'11_iknow-formula-text-contribution'/ds/'results',BASE/'03_AAKV_table/results/fixed_iKnow'/ds)
 tree(R/'25g_RawTriple_FS_control'/ds,BASE/'03_AAKV_table/results/full_system_raw'/ds,{'metrics.json','metrics.csv','protocol.json','samples.json','predictions.npz','progress.json'})
for name in ['01_Direct_Raw_AAKV_full_system.csv','02_AAKV_paired_comparisons.csv','REPORT.md','summary_complete.json']:
 cp(R/'25g_RawTriple_FS_control'/name,BASE/'03_AAKV_table/results'/name)

# 04 Selector: exact standalone selector runner and all complete outputs.
code_with_local_runtime(R/'26_relation_selection_AAKV_control/code/task26_relation_selection.py',BASE/'04_Selector_table/code/run_relation_selection_comparison.py')
cp(R/'26_relation_selection_AAKV_control/code/task26_finalize.py',BASE/'04_Selector_table/code/build_selector_table_and_statistics.py')
cp(R/'27_final_manuscript_tables/Table4_relation_selector.csv',BASE/'04_Selector_table/results/Table4_relation_selector.csv')
for ds in SETS:tree(R/'26_relation_selection_AAKV_control'/ds,BASE/'04_Selector_table/results/per_sample'/ds,{'metrics.json','metrics.csv','protocol.json','samples.json','progress.json'})
for name in ['01_all_metrics.csv','02_paired_statistics.csv','REPORT.md','summary_complete.json']:
 cp(R/'26_relation_selection_AAKV_control'/name,BASE/'04_Selector_table/results'/name)

# 05 Parameter table: source validation grid, selected config, and deterministic generator.
cp(R/'27_final_manuscript_tables/generate_final_paper_tables.py',BASE/'05_parameter_table/code/generate_parameter_and_protocol_table.py')
cp(R/'25_final_experiment_alpha03_Nr5/validation/DCASE_grid.csv',BASE/'05_parameter_table/results/DCASE_development_grid.csv')
cp(R/'25_final_experiment_alpha03_Nr5/validation/selected_config.json',BASE/'05_parameter_table/results/selected_config.json')
cp(R/'27_final_manuscript_tables/Table5_parameters_and_protocol.csv',BASE/'05_parameter_table/results/Table5_parameters_and_protocol.csv')

common='''
## Frozen external inputs

The code is complete and does not import another task's runner. It reads the following immutable research assets:

- audio and labels under `/data/zkx/zkx/iknow-audio/data`;
- CLAP model files under the project model directory;
- RotatE model `/data/zkx/zkx/iknow-audio/KGE_models/001`;
- frozen audio/text tensors in `/data/zkx/zkx/review1/12_shared-abcd-statistics`;
- static KG relation-tail cache in `/data/zkx/zkx/review1/18a_relation_oracle_audit`;
- frozen AAKV dictionary `/data/zkx/zkx/review1/20A_topP5_aligned_selector_exploration/aakv_all.json`.

These are data/model inputs, not imported experiment logic. Every computational folder contains its own copy of each dataset runtime.

## Frozen protocol

One hop; K=5; M=3; alpha=0.3; Nr=5 when Selector is enabled; kappa=100; Top-P disabled; seed 42 plus SHA256(audio path). DCASE17-T4 is development-only and is not included in the five test datasets.
'''
details={
'01_main_table':'''## Comparison\nCLAP, Frozen-iKnow, and the complete AAKV+Fusion+Selector method. `run_main_experiment.py` computes all branches independently from the immutable CLAP score vector in one sample pass.\n''',
'02_ablation_table':'''## Comparison\nThe complete 2^3 design: iKnow, AAKV only, Fusion only, Selector only, all three two-module combinations, and the complete method. No branch consumes another branch's modified scores.\n''',
'03_AAKV_table':'''## Comparison\nPanel A holds frozen relations and iKnow aggregation fixed while changing verbalization. Panel B uses the same Fusion+Selector algorithm and changes the verbalization module. Changing text can legitimately change Selector outputs; therefore Panel B is an end-to-end verbalization effect, while Panel A is the strict text-only control.\n''',
'04_Selector_table':'''## Comparison\nAll methods use AAKV and the same Fusion. Only relation choice changes: frozen Rq, static frequency Top-5, Random5 with seeds 42/43/44, or sample-level label-free Selector5. Ground truth is used only by the evaluator.\n''',
'05_parameter_table':'''## Comparison\nDocuments parameter meanings and provenance. Alpha=0.3 and Nr=5 are selected once on the 419-sample DCASE development set by MRR. The five final test datasets do not select parameters.\n'''}
for folder,title in folders.items():
 write(BASE/folder/'README.md',f'# {folder}: {title}\n\n'+details[folder]+common)

manifest={'package_root':str(BASE),'tables':folders,'datasets':[x for x in SETS],
          'result_policy':'copied byte-for-byte from completed frozen runs; no metric was recomputed by hand',
          'code_policy':'complete executed implementations copied locally; computational runners use packaged runtime code and declared immutable model/data artifacts'}
write(BASE/'MANIFEST.json',json.dumps(manifest,ensure_ascii=False,indent=2))
write(BASE/'README.md','# Final experiment package\n\nFive independently documented table folders. Start from each folder README. `MANIFEST.json` records scope and provenance.\n')
print(BASE)
