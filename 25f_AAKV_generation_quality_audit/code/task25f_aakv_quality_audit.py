#!/usr/bin/env python3
"""Task25(f): AAKV generation quality, stratified review sample, and interaction analysis."""
import csv
import hashlib
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from scipy.stats import binomtest


ROOT = Path("/data/zkx/zkx/review1")
AAKV = ROOT / "10_hard-prefix-pilot"
TASK25 = ROOT / "25_final_experiment_alpha03_Nr5" / "test"
OUT = ROOT / "25f_AAKV_generation_quality_audit"
DATASETS = [
    ("01_ESC50", "ESC-50"),
    ("02_UrbanSound8K", "UrbanSound8K"),
    ("03_FSD50K", "FSD50K"),
    ("04_DCASE17_T4", "DCASE17-T4"),
    ("05_AudioSet", "AudioSet"),
    ("06_TUT2017", "TUT2017"),
]
TEST_DATASETS = [x for x in DATASETS if x[0] != "04_DCASE17_T4"]
REPS = 10000


def norm(text):
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", str(text).lower().replace("_", " "))).strip()


def covered(entity, sentence):
    return norm(entity) in norm(sentence)


def percentile_ci(values):
    return np.percentile(np.asarray(values, dtype=float), [2.5, 97.5])


def bootstrap_interaction(arrays, seed, expression):
    rng = np.random.default_rng(seed)
    n = len(next(iter(arrays.values())))
    hit_values, rr_values = [], []
    for start in range(0, REPS, 250):
        z = min(250, REPS - start)
        idx = rng.integers(0, n, size=(z, n))
        hit_values.append(expression({k: (v[idx] == 1).astype(float) for k, v in arrays.items()}).mean(1) * 100)
        rr_values.append(expression({k: 1.0 / v[idx] for k, v in arrays.items()}).mean(1) * 100)
    return percentile_ci(np.concatenate(hit_values)), percentile_ci(np.concatenate(rr_values))


def choose_review_rows(rows, n, seed):
    """Deterministic outcome/relation-aware sample without using performance labels."""
    rng = np.random.default_rng(seed)
    buckets = defaultdict(list)
    for i, row in enumerate(rows):
        buckets[(row.get("verification_outcome", "unknown"), row.get("relation", "unknown"))].append(i)
    for values in buckets.values():
        rng.shuffle(values)
    selected = []
    keys = sorted(buckets, key=lambda x: (x[0], x[1]))
    while len(selected) < min(n, len(rows)):
        progressed = False
        for key in keys:
            if buckets[key] and len(selected) < n:
                selected.append(buckets[key].pop())
                progressed = True
        if not progressed:
            break
    return [rows[i] for i in selected]


OUT.mkdir(parents=True, exist_ok=True)
automatic_rows = []
review_rows = []
all_aakv_rows = []
system_prompts = {}

for ds, name in DATASETS:
    path = AAKV / ds / "prompts" / "qwen_generation_audit.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = payload["rows"]
    all_aakv_rows.extend((name, row) for row in rows)
    system_prompts[name] = payload.get("system_prompt", "")
    outcomes = Counter(row.get("verification_outcome", "unknown") for row in rows)
    texts = [str(row.get("qwen_verified", "")).strip() for row in rows]
    norms = [norm(x) for x in texts]
    word_counts = [len(x.split()) for x in texts]
    head_ok = [covered(row["head"], row.get("qwen_verified", "")) for row in rows]
    tail_ok = [covered(row["tail"], row.get("qwen_verified", "")) for row in rows]
    prefix_ok = [norm(row.get("qwen_verified", "")).startswith(norm(f"The sound of {row['head']}")) for row in rows]
    unique_texts = len(set(norms))
    automatic_rows.append({
        "dataset": name,
        "unique_triples": len(rows),
        "accepted_first_n": outcomes.get("accepted_first", 0),
        "accepted_first_pct": 100 * outcomes.get("accepted_first", 0) / len(rows),
        "accepted_repair_n": outcomes.get("accepted_repair", 0),
        "accepted_repair_pct": 100 * outcomes.get("accepted_repair", 0) / len(rows),
        "fallback_n": outcomes.get("universal_fallback", 0) + outcomes.get("manual_template_fallback", 0),
        "fallback_pct": 100 * (outcomes.get("universal_fallback", 0) + outcomes.get("manual_template_fallback", 0)) / len(rows),
        "head_preserved_pct": 100 * np.mean(head_ok),
        "tail_preserved_pct": 100 * np.mean(tail_ok),
        "exact_audio_prefix_pct": 100 * np.mean(prefix_ok),
        "unique_text_pct": 100 * unique_texts / len(rows),
        "duplicate_text_n": len(rows) - unique_texts,
        "mean_words": float(np.mean(word_counts)),
        "median_words": float(np.median(word_counts)),
        "max_words": max(word_counts),
    })
    sampled = choose_review_rows(rows, 30, 20260911 + int(hashlib.sha256(name.encode()).hexdigest()[:8], 16))
    for j, row in enumerate(sampled, 1):
        review_rows.append({
            "dataset": name,
            "review_id": f"{ds}-{j:02d}",
            "head": row["head"],
            "relation": row["relation"],
            "tail": row["tail"],
            "AAKV_text": row.get("qwen_verified", ""),
            "generation_outcome": row.get("verification_outcome", "unknown"),
            "head_preserved_auto": covered(row["head"], row.get("qwen_verified", "")),
            "tail_preserved_auto": covered(row["tail"], row.get("qwen_verified", "")),
            "human_relation_faithful_YN": "",
            "human_direction_correct_YN": "",
            "human_hallucination_present_YN": "",
            "human_acceptable_YN": "",
            "human_notes": "",
        })


interaction_rows = []
case_rows = []
flip_rows = []
confidence_rows = []
for ds, name in TEST_DATASETS:
    samples = json.loads((TASK25 / ds / "samples.json").read_text(encoding="utf-8"))
    ranks = {method: np.asarray([x["ranks"][method] for x in samples], dtype=float) for method in
             ["I_iKnow", "T_AAKV", "F_Fusion", "S_Selector", "TF", "TS", "FS", "TFS_Final"]}
    expressions = {
        "AAKV_main_effect_alone_T_minus_I": lambda x: x["T_AAKV"] - x["I_iKnow"],
        "AAKV_added_to_Fusion_TF_minus_F": lambda x: x["TF"] - x["F_Fusion"],
        "AAKV_added_to_Selector_TS_minus_S": lambda x: x["TS"] - x["S_Selector"],
        "AAKV_added_to_FusionSelector_TFS_minus_FS": lambda x: x["TFS_Final"] - x["FS"],
        "AAKV_x_Fusion_interaction_TF-T-F+I": lambda x: x["TF"] - x["T_AAKV"] - x["F_Fusion"] + x["I_iKnow"],
        "AAKV_x_Selector_interaction_TS-T-S+I": lambda x: x["TS"] - x["T_AAKV"] - x["S_Selector"] + x["I_iKnow"],
        "three_way_interaction": lambda x: x["TFS_Final"] - x["TF"] - x["TS"] - x["FS"] + x["T_AAKV"] + x["F_Fusion"] + x["S_Selector"] - x["I_iKnow"],
    }
    for label, expression in expressions.items():
        point_hit = float(expression({k: (v == 1).astype(float) for k, v in ranks.items()}).mean() * 100)
        point_rr = float(expression({k: 1.0 / v for k, v in ranks.items()}).mean() * 100)
        seed = 20260911 + int(hashlib.sha256(f"{name}|{label}".encode()).hexdigest()[:8], 16)
        hit_ci, rr_ci = bootstrap_interaction(ranks, seed, expression)
        interaction_rows.append({
            "dataset": name,
            "contrast": label,
            "effect_Hit@1_pp": point_hit,
            "Hit@1_CI95_low": float(hit_ci[0]),
            "Hit@1_CI95_high": float(hit_ci[1]),
            "effect_MRR_pp": point_rr,
            "MRR_CI95_low": float(rr_ci[0]),
            "MRR_CI95_high": float(rr_ci[1]),
            "CI_supports_positive_effect_Hit@1": bool(hit_ci[0] > 0),
            "CI_supports_positive_effect_MRR": bool(rr_ci[0] > 0),
        })
    for baseline, method, label in [
        ("I_iKnow", "T_AAKV", "AAKV under fixed relations: T vs I"),
        ("S_Selector", "TS", "AAKV after selection: TS vs S"),
        ("FS", "TFS_Final", "AAKV after fusion+selection: TFS vs FS"),
    ]:
        before = ranks[baseline] == 1
        after = ranks[method] == 1
        rescued = int(np.sum((~before) & after))
        harmed = int(np.sum(before & (~after)))
        discordant = rescued + harmed
        p = float(binomtest(min(rescued, harmed), discordant, 0.5).pvalue) if discordant else 1.0
        flip_rows.append({
            "dataset": name,
            "contrast": label,
            "wrong_to_correct": rescued,
            "correct_to_wrong": harmed,
            "net_rescued": rescued - harmed,
            "McNemar_exact_p": p,
        })
    votes = np.asarray([x.get("selected", {}).get("TS", {}).get("votes", 0) for x in samples], dtype=float)
    q25, q75 = np.quantile(votes, [0.25, 0.75])
    strata = {
        "low_consensus_bottom25": votes <= q25,
        "middle50": (votes > q25) & (votes < q75),
        "high_consensus_top25": votes >= q75,
    }
    delta_hit_selected = (ranks["TS"] == 1).astype(float) - (ranks["S_Selector"] == 1).astype(float)
    delta_rr_selected = 1.0 / ranks["TS"] - 1.0 / ranks["S_Selector"]
    for stratum, mask in strata.items():
        confidence_rows.append({
            "dataset": name,
            "selector_consensus_stratum": stratum,
            "n": int(mask.sum()),
            "vote_min": float(votes[mask].min()),
            "vote_max": float(votes[mask].max()),
            "AAKV_effect_TS_minus_S_Hit@1_pp": float(delta_hit_selected[mask].mean() * 100),
            "AAKV_effect_TS_minus_S_MRR_pp": float(delta_rr_selected[mask].mean() * 100),
        })
    candidates = [x for x in samples if x["ranks"]["T_AAKV"] > 1 and x["ranks"]["TS"] == 1]
    candidates.sort(key=lambda x: (x["ranks"]["T_AAKV"], x["sample_index"]), reverse=True)
    for row in candidates[:10]:
        case_rows.append({
            "dataset": name,
            "sample_index": row["sample_index"],
            "audio_path": row["audio_path"],
            "true_indices": json.dumps(row["true_indices"]),
            "iKnow_rank": row["ranks"]["I_iKnow"],
            "AAKV_only_rank": row["ranks"]["T_AAKV"],
            "Selector_only_rank": row["ranks"]["S_Selector"],
            "AAKV_plus_Selector_rank": row["ranks"]["TS"],
            "Full_TFS_rank": row["ranks"]["TFS_Final"],
            "TS_selected_relations": json.dumps(row.get("selected", {}).get("TS", {}).get("relations", []), ensure_ascii=False),
        })


def write_csv(path, rows):
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


write_csv(OUT / "01_AAKV_automatic_quality_summary.csv", automatic_rows)
write_csv(OUT / "02_stratified_manual_review_sheet_180.csv", review_rows)
write_csv(OUT / "03_AAKV_interaction_bootstrap.csv", interaction_rows)
write_csv(OUT / "04_AAKV_selector_rescue_cases.csv", case_rows)
write_csv(OUT / "06_AAKV_prediction_flips.csv", flip_rows)
write_csv(OUT / "07_AAKV_effect_by_selector_consensus.csv", confidence_rows)
(OUT / "05_actual_AAKV_system_prompt.txt").write_text(next(iter(system_prompts.values())), encoding="utf-8")

prompt_hashes = {name: hashlib.sha256(text.encode()).hexdigest() for name, text in system_prompts.items()}
protocol = {
    "completed_automatic_parts": True,
    "manual_review_status": "180-row stratified sheet prepared; human semantic judgments intentionally left blank",
    "AAKV_source": str(AAKV),
    "task25_source": str(TASK25),
    "automatic_unit": "unique KG triple verbalization",
    "manual_sample": {"n_per_dataset": 30, "total": len(review_rows), "strata": "generation outcome x relation", "label_free_sampling": True},
    "bootstrap": {"paired": True, "unit": "audio sample", "repetitions": REPS, "CI": "percentile 95%"},
    "prompt_hashes": prompt_hashes,
    "known_missing_control": "RawTriple + Fusion + Selector is not present in Task25; Direct + Fusion + Selector is FS and is present.",
}
(OUT / "protocol.json").write_text(json.dumps(protocol, ensure_ascii=False, indent=2), encoding="utf-8")

lines = [
    "# Task25(f): AAKV generation-quality and interaction audit",
    "",
    "## Automatic generation audit",
    "",
    "| Dataset | triples | first pass | repaired | fallback | head kept | tail kept | exact prefix | duplicate texts | median words |",
    "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
]
for x in automatic_rows:
    lines.append(
        f"| {x['dataset']} | {x['unique_triples']} | {x['accepted_first_pct']:.2f}% | "
        f"{x['accepted_repair_pct']:.2f}% | {x['fallback_pct']:.2f}% | {x['head_preserved_pct']:.2f}% | "
        f"{x['tail_preserved_pct']:.2f}% | {x['exact_audio_prefix_pct']:.2f}% | {x['duplicate_text_n']} | {x['median_words']:.1f} |"
    )
lines += [
    "",
    "## Interaction interpretation",
    "",
    "Effects are paired within the same audio samples. Positive interaction means the joint effect exceeds additive component effects; a CI crossing zero is only a trend.",
    "",
    "| Dataset | contrast | dHit@1 [95% CI] | dMRR [95% CI] |",
    "|---|---|---:|---:|",
]
for x in interaction_rows:
    lines.append(
        f"| {x['dataset']} | {x['contrast']} | {x['effect_Hit@1_pp']:+.3f} "
        f"[{x['Hit@1_CI95_low']:+.3f}, {x['Hit@1_CI95_high']:+.3f}] | "
        f"{x['effect_MRR_pp']:+.3f} [{x['MRR_CI95_low']:+.3f}, {x['MRR_CI95_high']:+.3f}] |"
    )
lines += [
    "",
    "## Evidence boundary",
    "",
    "- Task11 already compares Direct, RawTriple, generic Qwen and AAKV under the same frozen one-hop iKnow aggregation.",
    "- Task25 contains Direct + Fusion + Selector as `FS`, so the full AAKV method can be compared with the same method using Direct text (`TFS_Final` versus `FS`).",
    "- Task25 does not contain RawTriple + Fusion + Selector. If the manuscript claims AAKV is superior to RawTriple inside the complete system, one additional frozen `Raw-FS` control is required.",
    "- The manual semantic audit is not fabricated: the 180 rows are prepared, but relation-faithfulness, direction and hallucination judgments remain for human review.",
    "",
    "## Mechanism-oriented diagnostics",
    "",
    "`06_AAKV_prediction_flips.csv` compares AAKV wrong-to-correct versus correct-to-wrong transitions before and after selection. `07_AAKV_effect_by_selector_consensus.csv` reports the AAKV increment within low/middle/high selector-consensus strata. Consensus is a selector-confidence proxy, not ground-truth relevance, so these analyses support but do not prove a causal noise-reduction mechanism.",
]
(OUT / "REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
(OUT / "progress.json").write_text(json.dumps({
    "automatic_audit_complete": True,
    "interaction_analysis_complete": True,
    "rescue_cases_complete": True,
    "manual_review_sheet_prepared": True,
    "manual_review_completed": False,
}, indent=2), encoding="utf-8")

print((OUT / "REPORT.md").read_text(encoding="utf-8"))
