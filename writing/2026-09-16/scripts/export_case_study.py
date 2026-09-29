from pathlib import Path
import csv
import json
import numpy as np

LATEX = Path(__file__).resolve().parents[1]
PACKAGE = Path(r"C:\Users\zkx\Desktop\论文修改\任务清单\final_experiment_package")
MAP = Path(r"C:\Users\zkx\Desktop\论文修改\任务清单\核验结果\实体映射v2严格版\entity_mapping_v2_full_audit.csv")
SRC = PACKAGE / "01_main_table" / "results" / "per_sample" / "01_ESC50"
OUT = LATEX / "figures" / "further_analysis" / "representative_cases.csv"
EVIDENCE = LATEX / "figures" / "further_analysis" / "case_evidence_export_ESC50.json"

with MAP.open(encoding="utf-8-sig", newline="") as f:
    labels = sorted({r["source_dataset_label"].replace("_", " ")
                     for r in csv.DictReader(f) if r["dataset"] == "esc50"})

rows = json.loads((SRC / "samples.json").read_text(encoding="utf-8"))
pred = np.load(SRC / "predictions.npz", allow_pickle=True)
methods = pred["methods"].tolist()
scores = pred["scores"]
bi, fi = methods.index("I_iKnow"), methods.index("TFS_Final")

candidates = []
for i, row in enumerate(rows):
    br, fr = row["ranks"]["I_iKnow"], row["ranks"]["TFS_Final"]
    kind = None
    if br > 1 and fr == 1:
        kind = "wrong_to_correct"
    elif br > fr > 1:
        kind = "rank_improved"
    elif br == 1 and fr > 1:
        kind = "correct_to_wrong"
    if kind:
        candidates.append({
            "case_type": kind,
            "sample_index": i,
            "audio_file": Path(row["audio_path"]).name,
            "true_class": labels[row["true_indices"][0]],
            "iknow_prediction": labels[int(np.argmax(scores[i, bi]))],
            "final_prediction": labels[int(np.argmax(scores[i, fi]))],
            "iknow_true_rank": br,
            "final_true_rank": fr,
            "selected_relations": "; ".join(row["selected"]["TFS_Final"]["relations"]),
        })

chosen = [
    max((r for r in candidates if r["case_type"] == "wrong_to_correct"),
        key=lambda r: r["iknow_true_rank"]),
    max((r for r in candidates if r["case_type"] == "rank_improved"),
        key=lambda r: 1/r["final_true_rank"] - 1/r["iknow_true_rank"]),
    max((r for r in candidates if r["case_type"] == "correct_to_wrong"),
        key=lambda r: r["final_true_rank"]),
]

if EVIDENCE.exists():
    evidence_by_index = {
        row["sample_index"]: row for row in json.loads(EVIDENCE.read_text(encoding="utf-8"))
    }
    for row in chosen:
        evidence = evidence_by_index.get(row["sample_index"], {})
        row["consensus_class"] = evidence.get("consensus_class", "")
        row["evidence_summary_rule"] = evidence.get("compact_evidence_rule", "")
        row["representative_aakv_evidence"] = " | ".join(
            item["aakv_text"] for item in evidence.get("compact_evidence", [])
            if item.get("aakv_text")
        )
        row["all_evidence_count"] = len(evidence.get("all_evidence", []))

with OUT.open("w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(chosen[0]))
    w.writeheader(); w.writerows(chosen)

print(OUT)
