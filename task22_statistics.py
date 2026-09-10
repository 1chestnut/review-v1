#!/usr/bin/env python3
"""Task 22: paired bootstrap CIs and exact McNemar tests for Task 21."""
import csv
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy.stats import binomtest

ROOT = Path('/data/zkx/zkx/review1')
SOURCE = ROOT / '21_noTopP_factorial_vs_frozen_iKnow'
OUT = ROOT / '22_paired_statistics_task21'
BOOTSTRAPS = 10_000
BOOTSTRAP_SEED = 2026

BASELINE = 'I_Frozen-iKnow-05b'
COMPARISONS = {
    'F-vs-iKnow': 'F_Fusion-only',
    'S-vs-iKnow': 'S_Selector-only',
    'TFS-vs-iKnow': 'TFS_AAKV+Fusion+Selector',
}
DATASETS = [
    ('01_ESC50', 'ESC-50'),
    ('02_UrbanSound8K', 'UrbanSound8K'),
    ('03_FSD50K', 'FSD50K'),
    ('04_DCASE17_T4', 'DCASE17-T4'),
    ('05_AudioSet', 'AudioSet'),
    ('06_TUT2017', 'TUT2017'),
]


def paired_bootstrap(delta_hit, delta_rr, seed, n_boot=BOOTSTRAPS, chunk=250):
    """Percentile paired bootstrap; both methods always receive identical sampled rows."""
    rng = np.random.default_rng(seed)
    n = len(delta_hit)
    hit_means, rr_means = [], []
    remaining = n_boot
    while remaining:
        size = min(chunk, remaining)
        indices = rng.integers(0, n, size=(size, n), endpoint=False)
        hit_means.append(delta_hit[indices].mean(axis=1) * 100.0)
        rr_means.append(delta_rr[indices].mean(axis=1) * 100.0)
        remaining -= size
    hit_samples = np.concatenate(hit_means)
    rr_samples = np.concatenate(rr_means)
    return (
        np.percentile(hit_samples, [2.5, 97.5]).tolist(),
        np.percentile(rr_samples, [2.5, 97.5]).tolist(),
    )


def holm_adjust(p_values):
    """Holm family-wise error correction, returned in original order."""
    p = np.asarray(p_values, dtype=float)
    order = np.argsort(p)
    adjusted_sorted = np.maximum.accumulate((len(p) - np.arange(len(p))) * p[order])
    adjusted_sorted = np.minimum(adjusted_sorted, 1.0)
    adjusted = np.empty_like(adjusted_sorted)
    adjusted[order] = adjusted_sorted
    return adjusted.tolist()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    results, transitions = [], []

    for dataset_dir, dataset_name in DATASETS:
        sample_path = SOURCE / dataset_dir / 'samples.json'
        rows = json.loads(sample_path.read_text(encoding='utf-8'))
        base_ranks = np.asarray([row['ranks'][BASELINE] for row in rows], dtype=float)
        base_hit = (base_ranks == 1).astype(float)
        base_rr = 1.0 / base_ranks

        for comparison, method in COMPARISONS.items():
            new_ranks = np.asarray([row['ranks'][method] for row in rows], dtype=float)
            new_hit = (new_ranks == 1).astype(float)
            new_rr = 1.0 / new_ranks
            rescued = int(np.sum((base_hit == 0) & (new_hit == 1)))
            harmed = int(np.sum((base_hit == 1) & (new_hit == 0)))
            both_correct = int(np.sum((base_hit == 1) & (new_hit == 1)))
            both_wrong = int(np.sum((base_hit == 0) & (new_hit == 0)))
            discordant = rescued + harmed
            p_value = float(binomtest(min(rescued, harmed), discordant, 0.5, alternative='two-sided').pvalue) if discordant else 1.0
            stable_seed = BOOTSTRAP_SEED + int(hashlib.sha256(f'{dataset_name}|{comparison}'.encode()).hexdigest()[:8], 16)
            hit_ci, mrr_ci = paired_bootstrap(new_hit - base_hit, new_rr - base_rr, stable_seed)
            delta_hit = float((new_hit - base_hit).mean() * 100.0)
            delta_mrr = float((new_rr - base_rr).mean() * 100.0)
            results.append({
                'dataset': dataset_name, 'n': len(rows), 'comparison': comparison,
                'baseline': BASELINE, 'method': method,
                'delta_Hit@1_pp': delta_hit,
                'Hit@1_CI95_low': hit_ci[0], 'Hit@1_CI95_high': hit_ci[1],
                'wrong_to_correct': rescued, 'correct_to_wrong': harmed,
                'net_rescued': rescued - harmed, 'both_correct': both_correct,
                'both_wrong': both_wrong, 'discordant': discordant,
                'McNemar_exact_p': p_value,
                'delta_MRR_pp': delta_mrr,
                'MRR_CI95_low': mrr_ci[0], 'MRR_CI95_high': mrr_ci[1],
            })
            for row, b_rank, n_rank in zip(rows, base_ranks.astype(int), new_ranks.astype(int)):
                status = ('wrong_to_correct' if b_rank != 1 and n_rank == 1 else
                          'correct_to_wrong' if b_rank == 1 and n_rank != 1 else
                          'both_correct' if b_rank == 1 else 'both_wrong')
                transitions.append({
                    'dataset': dataset_name, 'comparison': comparison,
                    'sample_index': row['sample_index'], 'audio_path': row['audio_path'],
                    'true_indices': json.dumps(row['true_indices']),
                    'iKnow_rank': b_rank, 'new_rank': n_rank,
                    'delta_reciprocal_rank': 1.0/n_rank - 1.0/b_rank,
                    'Hit@1_transition': status,
                })

    adjusted = holm_adjust([row['McNemar_exact_p'] for row in results])
    for row, adj in zip(results, adjusted):
        row['McNemar_Holm_p_18'] = adj
        row['Hit@1_CI_excludes_zero'] = row['Hit@1_CI95_low'] > 0 or row['Hit@1_CI95_high'] < 0
        row['MRR_CI_excludes_zero'] = row['MRR_CI95_low'] > 0 or row['MRR_CI95_high'] < 0
        row['McNemar_significant_Holm_0.05'] = adj < 0.05

    with (OUT / 'task22_statistics.csv').open('w', newline='', encoding='utf-8-sig') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(results[0])); writer.writeheader(); writer.writerows(results)
    with (OUT / 'task22_sample_transitions.csv').open('w', newline='', encoding='utf-8-sig') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(transitions[0])); writer.writeheader(); writer.writerows(transitions)
    (OUT / 'task22_statistics.json').write_text(json.dumps({
        'protocol': {'source': str(SOURCE), 'bootstrap_repetitions': BOOTSTRAPS,
                     'bootstrap_seed_base': BOOTSTRAP_SEED, 'bootstrap_type': 'paired percentile',
                     'mcnemar': 'exact two-sided binomial', 'multiplicity': 'Holm across all 18 McNemar tests'},
        'results': results,
    }, ensure_ascii=False, indent=2), encoding='utf-8')

    report = ['# Task 22 paired statistical analysis', '',
              f'- Paired bootstrap: {BOOTSTRAPS:,} resamples; base seed {BOOTSTRAP_SEED}.',
              '- McNemar: exact two-sided test; Holm correction across all 18 comparisons.',
              '- Values are percentage-point differences relative to frozen iKnow-05b.', '',
              '| Dataset | Comparison | dHit@1 [95% CI] | rescued/harmed | McNemar p | Holm p | dMRR [95% CI] |',
              '|---|---|---:|---:|---:|---:|---:|']
    for r in results:
        report.append(f"| {r['dataset']} | {r['comparison']} | {r['delta_Hit@1_pp']:+.3f} "
                      f"[{r['Hit@1_CI95_low']:+.3f}, {r['Hit@1_CI95_high']:+.3f}] | "
                      f"{r['wrong_to_correct']}/{r['correct_to_wrong']} | {r['McNemar_exact_p']:.4g} | "
                      f"{r['McNemar_Holm_p_18']:.4g} | {r['delta_MRR_pp']:+.3f} "
                      f"[{r['MRR_CI95_low']:+.3f}, {r['MRR_CI95_high']:+.3f}] |")
    (OUT / 'TASK22_REPORT.md').write_text('\n'.join(report) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
