#!/usr/bin/env python3
"""Audit second-hop M2/P while keeping the frozen K5/M1=3 one-hop setup."""

import hashlib
import importlib.util
import json
import math
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
RUNTIME = HERE / "iknow_runtime.py"
RESULTS = HERE / "results"
CACHE = HERE / "cache"
PROGRESS = RESULTS / "progress.json"
RESULT_FILE = RESULTS / "mp_audit_results.json"
TABLE_FILE = RESULTS / "mp_audit_table.csv"

GAMMA = 0.85
FUSION_TOP_P = 5
ALPHA_MIN = 0.4
ALPHA_MAX = 0.8


def load_runtime():
    spec = importlib.util.spec_from_file_location("frozen_01_runtime", str(RUNTIME))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def metrics(ranks):
    x = np.asarray(ranks, dtype=np.float64)
    return {
        "Hit@1": float(100 * np.mean(x <= 1)),
        "Hit@3": float(100 * np.mean(x <= 3)),
        "Hit@5": float(100 * np.mean(x <= 5)),
        "MRR": float(100 * np.mean(1.0 / x)),
    }


def rank_of_true(scores, true_indices):
    order = torch.argsort(scores, descending=True).detach().cpu().tolist()
    return min(order.index(int(target)) + 1 for target in true_indices)


def normalized_lse(values, scale):
    if values.numel() == 0:
        raise ValueError("normalized_lse requires at least one value")
    return (torch.logsumexp(scale * values, dim=0) - math.log(values.numel())) / scale


def joint_lse(base_score, evidence_scores, scale):
    return normalized_lse(torch.cat([base_score.reshape(1), evidence_scores]), scale)


def dynamic_alpha(base_scores):
    confidence = float(torch.max(base_scores))
    return float(np.clip(ALPHA_MIN + (ALPHA_MAX - ALPHA_MIN) * confidence,
                         ALPHA_MIN, ALPHA_MAX))


def new_fusion(base_score, evidence_scores, alpha, scale):
    if evidence_scores.numel() == 0:
        return base_score
    keep = torch.argsort(evidence_scores, descending=True, stable=True)[:FUSION_TOP_P]
    pooled = normalized_lse(evidence_scores[keep], scale)
    return alpha * base_score + (1.0 - alpha) * pooled


def hash_payload(payload):
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()


def build_or_load_knowledge(base, kge, factory, labels, kg_classes):
    """Static KG prediction cache; it never uses audio or ground truth."""
    CACHE.mkdir(parents=True, exist_ok=True)
    knowledge_path = CACHE / "knowledge.json"
    signature = {
        "dataset": CONFIG["dataset"],
        "classes": labels,
        "kg_classes": kg_classes,
        "relations": CONFIG["relations"],
        "top_m1": 3,
        "top_m2_max": 3,
        "text": "class_name, tail",
        "same_relations_both_hops": True,
    }
    signature_hash = hash_payload(signature)
    if knowledge_path.exists():
        cached = json.loads(knowledge_path.read_text(encoding="utf-8"))
        if cached.get("signature_hash") == signature_hash:
            return cached

    base.TOP_M = int(CONFIG["top_m"])
    get_tails = base.build_tail_predictor(kge, factory)
    valid_relations = [r for r in CONFIG["relations"] if r in factory.relation_to_id]
    candidate_labels = {str(x).lower().strip() for x in labels}
    classes = []
    audit = {
        "head_unmapped": 0,
        "first_hop_queries": 0,
        "second_hop_queries": 0,
        "empty_first_hop_queries": 0,
        "empty_second_hop_queries": 0,
        "self_loops_removed": 0,
        "returns_to_origin_removed": 0,
        "candidate_labels_removed": 0,
        "duplicate_tails_removed": 0,
    }

    def filtered_add(store, tail, class_name, origin, current):
        norm = str(tail).lower().strip()
        if norm == str(current).lower().strip():
            audit["self_loops_removed"] += 1
            return
        if norm == str(origin).lower().strip():
            audit["returns_to_origin_removed"] += 1
            return
        if norm == str(class_name).lower().strip() or norm in candidate_labels:
            audit["candidate_labels_removed"] += 1
            return
        if norm in store:
            audit["duplicate_tails_removed"] += 1
            return
        store[norm] = str(tail)

    for class_name, kg_class in zip(labels, kg_classes):
        head = base.get_kg_entity(kg_class)
        query_head = base.resolve_head_query(head, factory)
        first = OrderedDict()
        second_m1 = OrderedDict()
        second_m3 = OrderedDict()
        paths_m1, paths_m3 = [], []
        if query_head not in factory.entity_to_id:
            audit["head_unmapped"] += 1
        else:
            for relation in valid_relations:
                tails = get_tails(head, relation)
                audit["first_hop_queries"] += 1
                if not tails:
                    audit["empty_first_hop_queries"] += 1
                for tail in tails:
                    filtered_add(first, tail, class_name, head, head)
            for middle in first.values():
                for relation in valid_relations:
                    tails = get_tails(middle, relation)
                    audit["second_hop_queries"] += 1
                    if not tails:
                        audit["empty_second_hop_queries"] += 1
                    for rank, tail in enumerate(tails[:3], start=1):
                        before = len(second_m3)
                        filtered_add(second_m3, tail, class_name, head, middle)
                        if len(second_m3) > before:
                            paths_m3.append({"head": head, "middle": middle,
                                             "relation": relation, "tail": str(tail),
                                             "kge_rank": rank})
                        if rank == 1:
                            before = len(second_m1)
                            filtered_add(second_m1, tail, class_name, head, middle)
                            if len(second_m1) > before:
                                paths_m1.append({"head": head, "middle": middle,
                                                 "relation": relation, "tail": str(tail),
                                                 "kge_rank": rank})
        first_texts = [f"{class_name}, {tail}" for tail in first.values()]
        first_norms = {text.lower().strip() for text in first_texts}
        def make_second_texts(store):
            output = []
            for tail in store.values():
                text = f"{class_name}, {tail}"
                if text.lower().strip() not in first_norms:
                    output.append(text)
            return output
        classes.append({
            "class_name": class_name,
            "kg_class": kg_class,
            "head": head,
            "first_hop_texts": first_texts,
            "second_hop_texts_m1": make_second_texts(second_m1),
            "second_hop_texts_m3": make_second_texts(second_m3),
            "paths_m1": paths_m1,
            "paths_m3": paths_m3,
        })
    payload = {
        "signature": signature,
        "signature_hash": signature_hash,
        "valid_relations": valid_relations,
        "classes": classes,
        "audit": audit,
    }
    knowledge_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2),
                              encoding="utf-8")
    return payload


def build_or_load_text_embeddings(base, clap, labels, knowledge, device):
    """Precompute all class/evidence text embeddings fairly for every method."""
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / "text_embeddings.pt"
    signature = hash_payload({
        "knowledge": knowledge["signature_hash"],
        "labels": labels,
        "clap": "2023",
    })
    if path.exists():
        saved = torch.load(path, map_location="cpu")
        if saved.get("signature") == signature:
            return saved["label_embeddings"].to(device), saved["evidence_embeddings"].to(device), saved["index"]

    all_texts = []
    text_to_id = {}
    index = []
    for item in knowledge["classes"]:
        one_ids, two_m1_ids, two_m3_ids = [], [], []
        for target, texts in ((one_ids, item["first_hop_texts"]),
                              (two_m1_ids, item["second_hop_texts_m1"]),
                              (two_m3_ids, item["second_hop_texts_m3"])):
            for text in texts:
                if text not in text_to_id:
                    text_to_id[text] = len(all_texts)
                    all_texts.append(text)
                target.append(text_to_id[text])
        index.append({"h1": one_ids, "h2_m1": two_m1_ids, "h2_m3": two_m3_ids})

    label_embeddings = F.normalize(
        base.get_safe_text_embeddings(clap, labels, device), dim=-1
    )
    chunks = []
    for start in range(0, len(all_texts), 128):
        chunks.append(F.normalize(
            base.get_safe_text_embeddings(clap, all_texts[start:start + 128], device),
            dim=-1,
        ))
    evidence_embeddings = torch.cat(chunks) if chunks else torch.empty(
        (0, label_embeddings.shape[1]), device=device
    )
    torch.save({
        "signature": signature,
        "label_embeddings": label_embeddings.cpu(),
        "evidence_embeddings": evidence_embeddings.cpu(),
        "index": index,
        "texts": all_texts,
    }, path)
    return label_embeddings, evidence_embeddings, index


def save_progress(next_index, ranks, rows, audit):
    RESULTS.mkdir(parents=True, exist_ok=True)
    temp = PROGRESS.with_suffix(".tmp")
    temp.write_text(json.dumps({
        "next_index": next_index, "ranks": ranks, "samples": rows,
        "audit": audit,
    }, ensure_ascii=False), encoding="utf-8")
    os.replace(temp, PROGRESS)


@torch.no_grad()
def main():
    RESULTS.mkdir(parents=True, exist_ok=True)
    base = load_runtime()
    device = base.DEVICE
    print(f"Starting frozen second-hop M2/P audit: {CONFIG['dataset']}", flush=True)
    clap = base.CLAP(version="2023", use_cuda=torch.cuda.is_available())
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        kge = torch.load(os.path.join(base.KGE_MODEL_DIR, "trained_model.pkl"),
                         map_location=device)
    kge.eval()
    factory = TriplesFactory.from_path(base.TRAIN_TRIPLES_PATH)
    dataset = base.load_dataset()
    labels = list(dataset["label_classes"])
    kg_classes = list(dataset["kg_classes"])
    samples = list(base.iter_samples(dataset))
    knowledge = build_or_load_knowledge(base, kge, factory, labels, kg_classes)
    label_emb, evidence_emb, evidence_index = build_or_load_text_embeddings(
        base, clap, labels, knowledge, device
    )

    top_k = int(CONFIG["top_k"])
    scale = float(CONFIG["logit_scale"])
    methods = ["CLAP", "iKnow-1st", "Ours-1st", "2nd-M1-P1", "2nd-M3-P1", "2nd-M3-PAll"]
    ranks = {name: [] for name in methods}
    rows = []
    audit = {
        "evaluated": 0, "skipped": 0, "topk_classes": 0,
        "empty_h1": 0, "h2_available": 0,
        "selected_h2_m1_p1": 0, "selected_h2_m3_p1": 0,
        "offered_h2_m3_pall": 0,
    }
    start_time = time.time()

    for sample_index, sample in enumerate(tqdm(samples, desc=CONFIG["dataset"], mininterval=10)):
        if not os.path.exists(sample["audio_path"]) or not sample["true_indices"]:
            audit["skipped"] += 1
            continue
        try:
            audio = F.normalize(
                base.to_tensor(clap.get_audio_embeddings([sample["audio_path"]]))
                .to(device).float(), dim=-1
            )
        except Exception:
            audit["skipped"] += 1
            continue
        base_scores = torch.matmul(audio, label_emb.T).squeeze(0)
        evidence_scores = torch.matmul(audio, evidence_emb.T).squeeze(0)
        top_indices = torch.argsort(base_scores, descending=True)[:top_k].tolist()
        alpha = dynamic_alpha(base_scores)
        score_vectors = {name: base_scores.clone() for name in methods}
        class_records = []
        for class_index in top_indices:
            audit["topk_classes"] += 1
            ids1 = evidence_index[class_index]["h1"]
            ids2_m1 = evidence_index[class_index]["h2_m1"]
            ids2_m3 = evidence_index[class_index]["h2_m3"]
            s1 = evidence_scores[ids1] if ids1 else torch.empty(0, device=device)
            s2_m1 = evidence_scores[ids2_m1] if ids2_m1 else torch.empty(0, device=device)
            s2_m3 = evidence_scores[ids2_m3] if ids2_m3 else torch.empty(0, device=device)
            if not ids1:
                audit["empty_h1"] += 1
            if ids2_m3:
                audit["h2_available"] += 1

            # Exact frozen 01 aggregation for the one-hop reproduction column.
            if s1.numel():
                score_vectors["iKnow-1st"][class_index] = joint_lse(
                    base_scores[class_index], s1, scale
                )
            score_vectors["Ours-1st"][class_index] = new_fusion(
                base_scores[class_index], s1, alpha, scale
            )

            def select_h2(scores, p):
                if scores.numel() == 0:
                    return scores
                decayed = GAMMA * scores
                if p == "all":
                    return decayed
                keep = torch.argsort(decayed, descending=True, stable=True)[:int(p)]
                return decayed[keep]

            h2_m1_p1 = select_h2(s2_m1, 1)
            h2_m3_p1 = select_h2(s2_m3, 1)
            h2_m3_all = select_h2(s2_m3, "all")
            for method, selected in (
                ("2nd-M1-P1", h2_m1_p1),
                ("2nd-M3-P1", h2_m3_p1),
                ("2nd-M3-PAll", h2_m3_all),
            ):
                score_vectors[method][class_index] = new_fusion(
                    base_scores[class_index], torch.cat([s1, selected]), alpha, scale
                )
            audit["selected_h2_m1_p1"] += int(h2_m1_p1.numel())
            audit["selected_h2_m3_p1"] += int(h2_m3_p1.numel())
            audit["offered_h2_m3_pall"] += int(h2_m3_all.numel())
            class_records.append({
                "class_index": class_index,
                "h1_count": len(ids1), "h2_m1_count": len(ids2_m1),
                "h2_m3_count": len(ids2_m3),
                "selected_m1_p1": int(h2_m1_p1.numel()),
                "selected_m3_p1": int(h2_m3_p1.numel()),
                "offered_m3_pall": int(h2_m3_all.numel()),
            })

        sample_ranks = {
            name: rank_of_true(scores, sample["true_indices"])
            for name, scores in score_vectors.items()
        }
        for name in methods:
            ranks[name].append(int(sample_ranks[name]))
        rows.append({
            "sample_index": sample_index,
            "audio_path": sample["audio_path"],
            "true_indices": [int(x) for x in sample["true_indices"]],
            "alpha": alpha,
            "ranks": sample_ranks,
            "topk": top_indices,
            "classes": class_records,
        })
        audit["evaluated"] += 1
        if audit["evaluated"] % 20 == 0:
            save_progress(sample_index + 1, ranks, rows, audit)

    metric_table = {name: metrics(values) for name, values in ranks.items()}
    comparisons = {}
    for newer, older in [
        ("Ours-1st", "iKnow-1st"),
        ("2nd-M1-P1", "Ours-1st"),
        ("2nd-M3-P1", "Ours-1st"),
        ("2nd-M3-PAll", "Ours-1st"),
        ("2nd-M3-P1", "2nd-M1-P1"),
        ("2nd-M3-PAll", "2nd-M3-P1"),
    ]:
        a, b = np.asarray(ranks[newer]), np.asarray(ranks[older])
        comparisons[f"{newer} minus {older}"] = {
            "delta_Hit@1": float(100 * np.mean((a <= 1).astype(float) - (b <= 1).astype(float))),
            "delta_MRR": float(100 * np.mean(1.0 / a - 1.0 / b)),
            "wrong_to_right": int(np.sum((b > 1) & (a == 1))),
            "right_to_wrong": int(np.sum((b == 1) & (a > 1))),
            "rank_improved": int(np.sum(a < b)),
            "rank_worsened": int(np.sum(a > b)),
        }
    protocol = {
        "status": "exploratory_only_not_final_test",
        "dataset": CONFIG["dataset"],
        "top_k": top_k, "top_m1": 3, "top_m2_values": [1, 3],
        "relations_both_hops": CONFIG["relations"],
        "knowledge_text_both_hops": "class_name, tail",
        "gamma": GAMMA, "second_hop_p_values": [1, "all"],
        "alpha": "clip(0.4 + 0.4 * max_CLAP_similarity, 0.4, 0.8)",
        "new_fusion": "alpha*base + (1-alpha)*LME100(TopP(evidence))",
        "second_hop_policy": "no gate; compare M2=1/P=1, M2=3/P=1, and M2=3/P=All",
        "frozen_fusion_top_p": FUSION_TOP_P,
        "cache": "static KG paths and CLAP text embeddings; no labels/audio used",
        "timing_valid": False,
        "config_sha256": hashlib.sha256((HERE / "config.json").read_bytes()).hexdigest(),
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    payload = {
        "completed": True,
        "protocol": protocol,
        "metrics": metric_table,
        "comparisons": comparisons,
        "knowledge_audit": knowledge["audit"],
        "run_audit": audit,
        "samples": rows,
        "elapsed_wall_seconds_shared_cache_runner": time.time() - start_time,
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    RESULT_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2),
                           encoding="utf-8")
    lines = ["method,Hit@1,Hit@3,Hit@5,MRR"]
    for name in methods:
        m = metric_table[name]
        lines.append(f"{name},{m['Hit@1']:.8f},{m['Hit@3']:.8f},{m['Hit@5']:.8f},{m['MRR']:.8f}")
    TABLE_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")
    save_progress(len(samples), ranks, rows, audit)
    print(json.dumps(metric_table, indent=2), flush=True)


if __name__ == "__main__":
    main()
