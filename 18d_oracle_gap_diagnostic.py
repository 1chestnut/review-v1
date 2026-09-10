#!/usr/bin/env python3
"""Offline Task 18D diagnostic using frozen Task18A/18C sample outputs."""

import csv
import json
from pathlib import Path


ROOT = Path("/data/zkx/zkx/review1")
A_ROOT = ROOT / "18a_relation_oracle_audit"
C_ROOT = ROOT / "18c_discriminative_relation_selector"
OUT_ROOT = ROOT / "18d_oracle_gap_diagnostic"


def pct(num, den):
    return 100.0 * num / den if den else 0.0


def load(path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main():
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    summaries = []
    for a_dir in sorted(p for p in A_ROOT.iterdir() if p.is_dir() and p.name[:2].isdigit()):
        c_dir = C_ROOT / a_dir.name
        a_path = a_dir / "results" / "relation_oracle_results.json"
        c_path = c_dir / "results" / "discriminative_selector_results.json"
        if not (a_path.exists() and c_path.exists()):
            continue
        a_data, c_data = load(a_path), load(c_path)
        a_rows = {row["audio_path"]: row for row in a_data["rows"]}
        c_rows = {row["audio_path"]: row for row in c_data["rows"]}
        common = sorted(set(a_rows) & set(c_rows))
        counts = {
            "n": len(common), "oracle_top1_cover": 0, "oracle_top3_cover": 0,
            "consensus_correct": 0, "oracle_better_than_frozen": 0,
            "cm1_recovers_oracle_opportunity": 0, "cm3_recovers_oracle_opportunity": 0,
            "cm1_equals_oracle_rank": 0, "cm3_equals_oracle_rank": 0,
            "cm1_worse_than_frozen": 0, "cm3_worse_than_frozen": 0,
            "opportunity_oracle_top1_cover": 0, "opportunity_oracle_top3_cover": 0,
            "opportunity_consensus_correct": 0,
        }
        detail = []
        for key in common:
            a, c = a_rows[key], c_rows[key]
            oracle = set(a["oracle_relations"])
            selected = c["selected_relations"]
            top1 = selected["Consensus-Margin-Top1"]
            top3 = selected["Consensus-Margin-Top3"]
            ranks = c["ranks"]
            frozen, oracle_rank = a["frozen_iknow_rank"], a["oracle_rank"]
            cm1, cm3 = ranks["Consensus-Margin-Top1"], ranks["Consensus-Margin-Top3"]
            true_set = set(a["true_indices"])
            opportunity = oracle_rank < frozen
            counts["oracle_top1_cover"] += bool(oracle.intersection(top1))
            counts["oracle_top3_cover"] += bool(oracle.intersection(top3))
            counts["consensus_correct"] += c["consensus_class_index"] in true_set
            counts["oracle_better_than_frozen"] += opportunity
            counts["opportunity_oracle_top1_cover"] += opportunity and bool(oracle.intersection(top1))
            counts["opportunity_oracle_top3_cover"] += opportunity and bool(oracle.intersection(top3))
            counts["opportunity_consensus_correct"] += opportunity and c["consensus_class_index"] in true_set
            counts["cm1_recovers_oracle_opportunity"] += opportunity and cm1 < frozen
            counts["cm3_recovers_oracle_opportunity"] += opportunity and cm3 < frozen
            counts["cm1_equals_oracle_rank"] += cm1 == oracle_rank
            counts["cm3_equals_oracle_rank"] += cm3 == oracle_rank
            counts["cm1_worse_than_frozen"] += cm1 > frozen
            counts["cm3_worse_than_frozen"] += cm3 > frozen
            detail.append({
                "audio_path": key, "frozen_rank": frozen, "oracle_rank": oracle_rank,
                "cm_top1_rank": cm1, "cm_top3_rank": cm3,
                "consensus_correct": c["consensus_class_index"] in true_set,
                "oracle_in_selected_top1": bool(oracle.intersection(top1)),
                "oracle_in_selected_top3": bool(oracle.intersection(top3)),
                "oracle_relations": "|".join(sorted(oracle)),
                "selected_top1": "|".join(top1), "selected_top3": "|".join(top3),
            })
        n, opp = counts["n"], counts["oracle_better_than_frozen"]
        summary = {
            "dataset": a_data["dataset"], **counts,
            "oracle_top1_coverage_pct": pct(counts["oracle_top1_cover"], n),
            "oracle_top3_coverage_pct": pct(counts["oracle_top3_cover"], n),
            "consensus_accuracy_pct": pct(counts["consensus_correct"], n),
            "oracle_opportunity_pct": pct(opp, n),
            "cm1_oracle_opportunity_recovery_pct": pct(counts["cm1_recovers_oracle_opportunity"], opp),
            "cm3_oracle_opportunity_recovery_pct": pct(counts["cm3_recovers_oracle_opportunity"], opp),
            "opportunity_oracle_top1_coverage_pct": pct(counts["opportunity_oracle_top1_cover"], opp),
            "opportunity_oracle_top3_coverage_pct": pct(counts["opportunity_oracle_top3_cover"], opp),
            "opportunity_consensus_accuracy_pct": pct(counts["opportunity_consensus_correct"], opp),
            "cm1_oracle_rank_match_pct": pct(counts["cm1_equals_oracle_rank"], n),
            "cm3_oracle_rank_match_pct": pct(counts["cm3_equals_oracle_rank"], n),
            "cm1_harm_pct": pct(counts["cm1_worse_than_frozen"], n),
            "cm3_harm_pct": pct(counts["cm3_worse_than_frozen"], n),
        }
        summaries.append(summary)
        ds_out = OUT_ROOT / a_dir.name
        ds_out.mkdir(exist_ok=True)
        with (ds_out / "sample_diagnostic.csv").open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=detail[0].keys())
            writer.writeheader(); writer.writerows(detail)
        (ds_out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    if not summaries:
        raise SystemExit("No matched Task18A/18C results found")
    with (OUT_ROOT / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=summaries[0].keys())
        writer.writeheader(); writer.writerows(summaries)
    (OUT_ROOT / "summary.json").write_text(json.dumps(summaries, indent=2), encoding="utf-8")
    print(json.dumps(summaries, indent=2))


if __name__ == "__main__":
    main()
