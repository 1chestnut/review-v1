#!/usr/bin/env python3
"""Merge Direct-FS, Raw-FS and AAKV-TFS and compute paired comparisons."""
import csv
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy.stats import binomtest


ROOT = Path("/data/zkx/zkx/review1")
TASK25 = ROOT / "25_final_experiment_alpha03_Nr5" / "test"
TASK = ROOT / "25g_RawTriple_FS_control"
DATASETS = [
    ("01_ESC50", "ESC-50"),
    ("02_UrbanSound8K", "UrbanSound8K"),
    ("03_FSD50K", "FSD50K"),
    ("05_AudioSet", "AudioSet"),
    ("06_TUT2017", "TUT2017"),
]


def metric(ranks):
    values = np.asarray(ranks, dtype=float)
    return {
        "Hit@1": float(100 * np.mean(values == 1)),
        "Hit@3": float(100 * np.mean(values <= 3)),
        "Hit@5": float(100 * np.mean(values <= 5)),
        "MRR": float(100 * np.mean(1.0 / values)),
    }


def paired_stats(a, b, seed, repetitions=10000):
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    ah, bh = (a == 1), (b == 1)
    rescued = int(np.sum((~ah) & bh))
    harmed = int(np.sum(ah & (~bh)))
    discordant = rescued + harmed
    p = float(binomtest(min(rescued, harmed), discordant, 0.5).pvalue) if discordant else 1.0
    rng = np.random.default_rng(seed)
    dh = bh.astype(float) - ah.astype(float)
    dr = 1.0 / b - 1.0 / a
    hit, rr = [], []
    for start in range(0, repetitions, 250):
        z = min(250, repetitions - start)
        idx = rng.integers(0, len(a), size=(z, len(a)))
        hit.append(dh[idx].mean(1) * 100)
        rr.append(dr[idx].mean(1) * 100)
    return {
        "delta_Hit@1_pp": float(dh.mean() * 100),
        "Hit@1_CI95_low": float(np.percentile(np.concatenate(hit), 2.5)),
        "Hit@1_CI95_high": float(np.percentile(np.concatenate(hit), 97.5)),
        "wrong_to_correct": rescued,
        "correct_to_wrong": harmed,
        "McNemar_exact_p": p,
        "delta_MRR_pp": float(dr.mean() * 100),
        "MRR_CI95_low": float(np.percentile(np.concatenate(rr), 2.5)),
        "MRR_CI95_high": float(np.percentile(np.concatenate(rr), 97.5)),
    }


main_rows, stat_rows = [], []
for dataset, name in DATASETS:
    frozen_rows = json.loads((TASK25 / dataset / "samples.json").read_text(encoding="utf-8"))
    raw_rows = json.loads((TASK / dataset / "samples.json").read_text(encoding="utf-8"))
    if len(frozen_rows) != len(raw_rows):
        raise RuntimeError(f"sample count mismatch for {name}")
    for old, new in zip(frozen_rows, raw_rows):
        if old["audio_path"] != new["audio_path"] or old["true_indices"] != new["true_indices"]:
            raise RuntimeError(f"sample identity mismatch for {name} at {old['sample_index']}")
    ranks = {
        "Direct-FS": [x["ranks"]["FS"] for x in frozen_rows],
        "Raw-FS": [x["rank"] for x in raw_rows],
        "AAKV-TFS": [x["ranks"]["TFS_Final"] for x in frozen_rows],
    }
    for method, values in ranks.items():
        current = metric(values)
        main_rows.append({"dataset": name, "method": method, **current})
    for baseline in ["Direct-FS", "Raw-FS"]:
        label = f"AAKV-TFS vs {baseline}"
        seed = 20260911 + int(hashlib.sha256(f"{name}|{label}".encode()).hexdigest()[:8], 16)
        stat_rows.append({
            "dataset": name,
            "comparison": label,
            **paired_stats(ranks[baseline], ranks["AAKV-TFS"], seed),
        })


def write_csv(path, rows):
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


write_csv(TASK / "01_Direct_Raw_AAKV_full_system.csv", main_rows)
write_csv(TASK / "02_AAKV_paired_comparisons.csv", stat_rows)
lines = [
    "# Task25(g): controlled text comparison inside the full system",
    "",
    "All three methods use the same Fusion and Selector. Only evidence text changes.",
    "",
    "| Dataset | Direct-FS Hit@1/MRR | Raw-FS Hit@1/MRR | AAKV-TFS Hit@1/MRR |",
    "|---|---:|---:|---:|",
]
for _, name in DATASETS:
    subset = {x["method"]: x for x in main_rows if x["dataset"] == name}
    cells = {k: f"{v['Hit@1']:.3f}/{v['MRR']:.3f}" for k, v in subset.items()}
    lines.append(f"| {name} | {cells['Direct-FS']} | {cells['Raw-FS']} | {cells['AAKV-TFS']} |")
lines += ["", "## Paired AAKV contrasts", "", "| Dataset | Comparison | dHit@1 [95% CI] | rescued/harmed | exact p | dMRR [95% CI] |", "|---|---|---:|---:|---:|---:|"]
for x in stat_rows:
    lines.append(
        f"| {x['dataset']} | {x['comparison']} | {x['delta_Hit@1_pp']:+.3f} "
        f"[{x['Hit@1_CI95_low']:+.3f},{x['Hit@1_CI95_high']:+.3f}] | "
        f"{x['wrong_to_correct']}/{x['correct_to_wrong']} | {x['McNemar_exact_p']:.4g} | "
        f"{x['delta_MRR_pp']:+.3f} [{x['MRR_CI95_low']:+.3f},{x['MRR_CI95_high']:+.3f}] |"
    )
(TASK / "REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
(TASK / "summary_complete.json").write_text(json.dumps({"completed": True, "datasets": [x[1] for x in DATASETS]}, indent=2), encoding="utf-8")
print((TASK / "REPORT.md").read_text(encoding="utf-8"))
