#!/usr/bin/env python3
"""Run only the frozen CLAP and one-hop iKnow-NormLSE reproduction."""

import importlib.util
import json
import os
import time
import warnings
from collections import OrderedDict
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from pykeen.triples import TriplesFactory
from tqdm import tqdm


HERE = Path(__file__).resolve().parent
CONFIG = json.loads((HERE / "config.json").read_text(encoding="utf-8"))
BASE_SCRIPT = HERE / "iknow_runtime.py"
RESULT_DIR = HERE / "results"
PROGRESS_FILE = RESULT_DIR / "progress.json"
RESULT_FILE = RESULT_DIR / "clap_iknow_results.json"
TABLE_FILE = RESULT_DIR / "clap_iknow_table.csv"
MAPPING_FILE = HERE.parent / "entity_mapping_v2.json"


def load_base():
    spec = importlib.util.spec_from_file_location(
        f"historical_{CONFIG['dataset']}_base", str(BASE_SCRIPT)
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def metrics(ranks):
    values = np.asarray(ranks, dtype=np.float64)
    return {
        "Hit@1": float(np.mean(values <= 1) * 100.0),
        "Hit@3": float(np.mean(values <= 3) * 100.0),
        "Hit@5": float(np.mean(values <= 5) * 100.0),
        "MRR": float(np.mean(1.0 / values) * 100.0),
    }


def normalized_lse(base_score, evidence_scores, scale):
    logits = torch.cat(
        [base_score.unsqueeze(0) * scale, evidence_scores * scale]
    )
    return (torch.logsumexp(logits, dim=0) - np.log(logits.numel())) / scale


def save_progress(next_index, baseline_ranks, iknow_ranks, rows, audit):
    RESULT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "next_index": next_index,
        "baseline_ranks": baseline_ranks,
        "iknow_ranks": iknow_ranks,
        "samples": rows,
        "audit": audit,
    }
    temporary = PROGRESS_FILE.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    os.replace(temporary, PROGRESS_FILE)


def load_progress():
    if not PROGRESS_FILE.exists():
        return 0, [], [], [], {
            "mapped_topk": 0,
            "unmapped_topk": 0,
            "valid_relation_queries": 0,
            "empty_relation_queries": 0,
            "prompt_count": 0,
            "skipped_samples": 0,
        }
    payload = json.loads(PROGRESS_FILE.read_text(encoding="utf-8"))
    return (
        int(payload["next_index"]),
        payload["baseline_ranks"],
        payload["iknow_ranks"],
        payload["samples"],
        payload["audit"],
    )


def main():
    print("Starting strict mapping v2: " + CONFIG["dataset"], flush=True)
    base = load_base()
    all_mapping = json.loads(MAPPING_FILE.read_text(encoding="utf-8"))
    dataset_mapping = all_mapping[CONFIG["dataset"]]
    device = base.DEVICE
    clap = base.CLAP(version="2023", use_cuda=torch.cuda.is_available())
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        kge = torch.load(
            os.path.join(base.KGE_MODEL_DIR, "trained_model.pkl"),
            map_location=device,
        )
    kge.eval()
    factory = TriplesFactory.from_path(base.TRAIN_TRIPLES_PATH)

    top_k = int(CONFIG["top_k"])
    top_m = int(CONFIG["top_m"])
    logit_scale = float(CONFIG["logit_scale"])
    relations = list(CONFIG["relations"])
    valid_relations = [r for r in relations if r in factory.relation_to_id]

    base.TOP_M = top_m
    get_tails = base.build_tail_predictor(kge, factory)

    dataset = base.load_dataset()
    labels = dataset["label_classes"]
    kg_classes = dataset["kg_classes"]
    class_labels_set = {str(name).lower() for name in labels}
    samples = list(base.iter_samples(dataset))
    label_embeddings = F.normalize(
        base.get_safe_text_embeddings(clap, labels, device), dim=-1
    )

    start, baseline_ranks, iknow_ranks, rows, audit = load_progress()
    for sample_index in tqdm(
        range(start, len(samples)),
        total=len(samples),
        initial=start,
        desc=CONFIG["dataset"],
        mininterval=10,
    ):
        sample = samples[sample_index]
        audio_path = sample["audio_path"]
        true_indices = sample["true_indices"]
        if not os.path.exists(audio_path) or not true_indices:
            audit["skipped_samples"] += 1
            save_progress(
                sample_index + 1, baseline_ranks, iknow_ranks, rows, audit
            )
            continue

        try:
            audio = F.normalize(
                base.to_tensor(clap.get_audio_embeddings([audio_path]))
                .to(device)
                .float(),
                dim=-1,
            )
        except Exception:
            audit["skipped_samples"] += 1
            save_progress(
                sample_index + 1, baseline_ranks, iknow_ranks, rows, audit
            )
            continue

        clap_scores = torch.matmul(audio, label_embeddings.T).squeeze(0)
        iknow_scores = clap_scores.clone()
        top_indices = torch.argsort(clap_scores, descending=True)[:top_k].tolist()
        baseline_rank = base.rank_of_true(clap_scores, true_indices)
        sample_prompt_count = 0

        for class_index in top_indices:
            class_name = labels[class_index]
            mapping_entry = dataset_mapping[str(labels[class_index])]
            kg_entity = mapping_entry["entity"]
            query_entity = kg_entity
            if query_entity not in factory.entity_to_id:
                audit["unmapped_topk"] += 1
                continue
            audit["mapped_topk"] += 1

            # Historical implementation: filter candidate-label tails and
            # deduplicate the same tail across all selected relations.
            tails = OrderedDict()
            for relation in valid_relations:
                predicted = get_tails(kg_entity, relation)
                if predicted:
                    audit["valid_relation_queries"] += 1
                else:
                    audit["empty_relation_queries"] += 1
                for tail in predicted:
                    tail_norm = str(tail).lower().strip()
                    if (
                        tail_norm == str(class_name).lower()
                        or tail_norm in class_labels_set
                    ):
                        continue
                    if tail_norm not in tails:
                        tails[tail_norm] = f"{class_name}, {tail}"

            if not tails:
                continue
            evidence_scores = base.score_prompt_list(
                clap, audio, list(tails.values())
            )
            iknow_scores[class_index] = normalized_lse(
                clap_scores[class_index], evidence_scores, logit_scale
            )
            sample_prompt_count += len(tails)

        iknow_rank = base.rank_of_true(iknow_scores, true_indices)
        baseline_ranks.append(int(baseline_rank))
        iknow_ranks.append(int(iknow_rank))
        audit["prompt_count"] += int(sample_prompt_count)
        rows.append(
            {
                "sample_index": sample_index,
                "audio_path": audio_path,
                "true_indices": [int(x) for x in true_indices],
                "clap_rank": int(baseline_rank),
                "iknow_rank": int(iknow_rank),
                "prompt_count": int(sample_prompt_count),
            }
        )
        if (sample_index + 1) % 20 == 0:
            save_progress(
                sample_index + 1, baseline_ranks, iknow_ranks, rows, audit
            )

    clap_metrics = metrics(baseline_ranks)
    iknow_metrics = metrics(iknow_ranks)
    payload = {
        "completed": True,
        "dataset": CONFIG["dataset"],
        "evaluated_samples": len(baseline_ranks),
        "protocol": {
            "depth": 1,
            "top_k": top_k,
            "top_m": top_m,
            "relations": relations,
            "valid_relations_in_kg": valid_relations,
            "knowledge_text": "class_name, tail",
            "tail_filtering": True,
            "cross_relation_tail_deduplication": True,
            "aggregation": "scaled evidence-count-normalized joint LSE",
            "entity_mapping": "strict frozen v2; unresolved keeps CLAP score",
            "logit_scale": logit_scale,
        },
        "metrics": {"CLAP": clap_metrics, "iKnow": iknow_metrics},
        "audit": audit,
        "samples": rows,
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    RESULT_DIR.mkdir(parents=True, exist_ok=True)
    RESULT_FILE.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    TABLE_FILE.write_text(
        "method,Hit@1,Hit@3,Hit@5,MRR\n"
        + "CLAP,{Hit@1:.8f},{Hit@3:.8f},{Hit@5:.8f},{MRR:.8f}\n".format(
            **clap_metrics
        )
        + "iKnow,{Hit@1:.8f},{Hit@3:.8f},{Hit@5:.8f},{MRR:.8f}\n".format(
            **iknow_metrics
        ),
        encoding="utf-8",
    )
    save_progress(len(samples), baseline_ranks, iknow_ranks, rows, audit)
    print(json.dumps(payload["metrics"], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
