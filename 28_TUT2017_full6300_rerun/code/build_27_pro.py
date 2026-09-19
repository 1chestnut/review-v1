#!/usr/bin/env python3
import csv
import json
import shutil
from pathlib import Path

import numpy as np

ROOT = Path('/data/zkx/zkx/review1')
OLD = ROOT / '27_final_manuscript_tables'
NEW = ROOT / '27-pro_final_manuscript_tables_TUT6300'
RERUN = ROOT / '28_TUT2017_full6300_rerun'
SETS = ['ESC-50', 'UrbanSound8K', 'FSD50K', 'AudioSet', 'TUT2017']
METRICS = ['Hit@1', 'Hit@3', 'Hit@5', 'MRR']


def read_csv(path):
    with path.open(encoding='utf-8-sig', newline='') as handle:
        return list(csv.DictReader(handle))


def write_csv(path, rows):
    fields = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    with path.open('w', encoding='utf-8-sig', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


if NEW.exists():
    shutil.rmtree(NEW)
shutil.copytree(OLD, NEW)

main = read_csv(RERUN / 'summary/01_main_results_full6300.csv')
write_csv(NEW / 'Table1_main_results.csv', main)

ablation = read_csv(RERUN / 'summary/02_ablation_full6300.csv')
methods = ['I_iKnow', 'T_AAKV', 'F_Fusion', 'S_Selector', 'TF', 'TS', 'FS', 'TFS_Final']
ablation = [r for r in ablation if r['dataset'] != 'MacroMean']
for method in methods:
    subset = [r for r in ablation if r['method'] == method]
    ablation.append({
        'dataset': 'MacroMean',
        'method': method,
        **{metric: float(np.mean([float(r[metric]) for r in subset])) for metric in METRICS},
    })
write_csv(NEW / 'Table2_factorial_ablation.csv', ablation)

# Table 3 Panel B can be updated completely from the rerun. Panel A is retained
# as an explicitly legacy auxiliary analysis because Task 28 did not rerun its
# fixed-iKnow Qwen-General branches; it must not be presented as a 6,300-clip result.
table3 = read_csv(OLD / 'Table3_AAKV_verbalization.csv')
table3 = [r for r in table3 if not (r['dataset'] == 'TUT2017' and r['panel'].startswith('B:'))]
main_tut = {r['method']: r for r in read_csv(RERUN / 'main/test/06_TUT2017/metrics.csv')}
raw_tut = read_csv(RERUN / 'raw/06_TUT2017/metrics.csv')[0]
for method, source in [('Direct-FS', main_tut['FS']), ('Raw-FS', raw_tut), ('AAKV-TFS', main_tut['TFS_Final'])]:
    table3.append({'panel': 'B: frozen Fusion+Selector system', 'dataset': 'TUT2017', 'method': method,
                   **{metric: source[metric] for metric in METRICS}})
write_csv(NEW / 'Table3_AAKV_verbalization.csv', table3)

selector = read_csv(RERUN / 'summary/03_selector_full6300.csv')
write_csv(NEW / 'Table4_relation_selector.csv', selector)

shutil.copy2(RERUN / 'statistics/01_primary_final_vs_iknow.csv', NEW / 'Table6_paired_statistics.csv')
shutil.copy2(RERUN / 'statistics/02_module_contrasts.csv', NEW / 'Table7_module_contrasts.csv')
shutil.copy2(RERUN / 'summary/04_TUT_module_effects.csv', NEW / 'TUT2017_module_effects_full6300.csv')

old_main = {r['method']: r for r in read_csv(OLD / 'Table1_main_results.csv') if r['dataset'] == 'TUT2017'}
new_main = {r['method']: r for r in main if r['dataset'] == 'TUT2017'}
comparison = []
for method in ['CLAP', 'I_iKnow', 'TFS_Final']:
    row = {'method': method}
    for metric in METRICS:
        old_value = float(old_main[method][metric])
        new_value = float(new_main[method][metric])
        row[f'old_{metric}'] = old_value
        row[f'new_{metric}'] = new_value
        row[f'delta_{metric}_pp'] = new_value - old_value
    comparison.append(row)
write_csv(NEW / 'TUT2017_old4680_vs_new6300.csv', comparison)

def fmt(value):
    return f'{float(value):.2f}'

lines = [
    '# 27-pro: final manuscript tables with complete TUT2017 (6,300 clips)', '',
    'This directory is independent of `27_final_manuscript_tables`; the original summary is unchanged.',
    'TUT2017 now combines the official development (4,680) and evaluation (1,620) partitions.', '',
    '## Table 1. Main results (%)', '',
    '| Dataset | Method | Hit@1 | Hit@3 | Hit@5 | MRR |',
    '|---|---|---:|---:|---:|---:|',
]
for row in main:
    lines.append(f"| {row['dataset']} | {row['method']} | {fmt(row['Hit@1'])} | {fmt(row['Hit@3'])} | {fmt(row['Hit@5'])} | {fmt(row['MRR'])} |")

lines += ['', '## Table 2. Factorial ablation (Hit@1 / MRR, %)', '',
          '| Dataset | iKnow | AAKV | Fusion | Selector | AAKV+Fusion | AAKV+Selector | Fusion+Selector | Full |',
          '|---|---:|---:|---:|---:|---:|---:|---:|---:|']
labels = ['I_iKnow', 'T_AAKV', 'F_Fusion', 'S_Selector', 'TF', 'TS', 'FS', 'TFS_Final']
for dataset in SETS + ['MacroMean']:
    data = {r['method']: r for r in ablation if r['dataset'] == dataset}
    cells = [f"{fmt(data[m]['Hit@1'])}/{fmt(data[m]['MRR'])}" for m in labels]
    lines.append('| ' + dataset + ' | ' + ' | '.join(cells) + ' |')

lines += ['', '## Table 3. AAKV verbalization, Panel B (same Fusion+Selector system)', '',
          '| Dataset | Direct-FS | Raw-FS | AAKV-TFS |', '|---|---:|---:|---:|']
for dataset in SETS:
    data = {r['method']: r for r in table3 if r['dataset'] == dataset and r['panel'].startswith('B:')}
    cells = [f"{fmt(data[m]['Hit@1'])}/{fmt(data[m]['MRR'])}" for m in ['Direct-FS', 'Raw-FS', 'AAKV-TFS']]
    lines.append('| ' + dataset + ' | ' + ' | '.join(cells) + ' |')

lines += ['', '## Table 4. Relation-selection comparison (Hit@1 / MRR, %)', '',
          '| Dataset | FrozenRq | Frequency5 | Random5 mean | Selector5 |', '|---|---:|---:|---:|---:|']
for dataset in SETS:
    data = {r['method']: r for r in selector if r['dataset'] == dataset}
    cells = [f"{fmt(data[m]['Hit@1'])}/{fmt(data[m]['MRR'])}" for m in ['AAKV-FrozenRq', 'AAKV-Frequency5', 'AAKV-Random5-mean', 'AAKV-Selector5']]
    lines.append('| ' + dataset + ' | ' + ' | '.join(cells) + ' |')

lines += ['', '## TUT2017 old-to-new audit', '',
          '| Method | old Hit@1 | new Hit@1 | delta | old MRR | new MRR | delta |',
          '|---|---:|---:|---:|---:|---:|---:|']
for row in comparison:
    lines.append(f"| {row['method']} | {row['old_Hit@1']:.2f} | {row['new_Hit@1']:.2f} | {row['delta_Hit@1_pp']:+.2f} | {row['old_MRR']:.2f} | {row['new_MRR']:.2f} | {row['delta_MRR_pp']:+.2f} |")

lines += ['', '## Integrity note', '',
          '- Tables 1, 2, 3 Panel B, 4, 6 and 7 use the complete 6,300-clip TUT2017 rerun.',
          '- Table 3 Panel A in the CSV is retained only as a legacy auxiliary result. Its TUT2017 row still uses 4,680 clips and must not be cited as a complete-data result unless those four branches are rerun.',
          '- Table 5 is unchanged because the development protocol and frozen parameters did not change.', '']
(NEW / 'FINAL_TABLES_27_PRO.md').write_text('\n'.join(lines), encoding='utf-8')

provenance = {
    'base_summary_preserved': str(OLD),
    'complete_TUT_source': str(RERUN),
    'TUT2017_sample_count': 6300,
    'updated_tables': ['Table1', 'Table2', 'Table3 Panel B', 'Table4', 'Table6', 'Table7'],
    'legacy_not_updated': ['Table3 Panel A TUT2017 row'],
}
(NEW / 'PROVENANCE_27_PRO.json').write_text(json.dumps(provenance, ensure_ascii=False, indent=2), encoding='utf-8')
(NEW / 'README.md').write_text(
    '# 27-pro final manuscript tables\n\n'
    'Independent update using the complete 6,300-clip TUT2017 protocol. The original Task 27 directory is not modified. '
    'Read `FINAL_TABLES_27_PRO.md` and `PROVENANCE_27_PRO.json` before manuscript use.\n',
    encoding='utf-8',
)
print(NEW)
