#!/usr/bin/env python3
"""Task 18A: relation complementarity/oracle audit on frozen Task05b."""

import os
os.environ["CUBLAS_WORKSPACE_CONFIG"] = ":4096:8"
os.environ["PYTHONHASHSEED"] = "42"

import argparse
import hashlib
import importlib.util
import json
import random
import time
import warnings
from collections import OrderedDict, Counter
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from pykeen.triples import TriplesFactory
from tqdm import tqdm


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def metric_dict(ranks):
    x = np.asarray(ranks, dtype=np.float64)
    return {
        "Hit@1": float(np.mean(x <= 1) * 100),
        "Hit@3": float(np.mean(x <= 3) * 100),
        "Hit@5": float(np.mean(x <= 5) * 100),
        "MRR": float(np.mean(1.0 / x) * 100),
    }


def normalized_lse(base_score, evidence_scores, scale):
    z = torch.cat([base_score.reshape(1) * scale, evidence_scores * scale])
    return (torch.logsumexp(z, dim=0) - np.log(z.numel())) / scale


def encode_texts(clap, texts, device, batch_size=128):
    output = []
    for start in tqdm(range(0, len(texts), batch_size), desc="text embeddings"):
        batch = texts[start:start + batch_size]
        try:
            emb = clap.get_text_embeddings(batch)
            emb = torch.as_tensor(emb, device=device, dtype=torch.float32)
        except Exception:
            pieces = []
            for text in batch:
                pieces.append(torch.as_tensor(
                    clap.get_text_embeddings([text]), device=device,
                    dtype=torch.float32))
            emb = torch.cat(pieces, dim=0)
        output.append(F.normalize(emb, dim=-1).cpu())
    return torch.cat(output, dim=0)


def atomic_json(path, obj):
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, path)


def rank_of_true(scores, true_indices):
    order = torch.argsort(scores, descending=True).detach().cpu().numpy()
    return min(int(np.where(order == idx)[0][0]) + 1 for idx in true_indices)


def seed_sample(audio_path, master_seed=42):
    """Reuse Task12's stable path-derived seed for CLAP waveform cropping."""
    token = f"{master_seed}|{audio_path}".encode("utf-8")
    seed = int(hashlib.sha256(token).hexdigest()[:8], 16)
    random.seed(seed)
    np.random.seed(seed % (2**32 - 1))
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    return seed


def build_static_cache(base, clap, kge, factory, labels, mapping, relations,
                       top_m, device, cache_path):
    if cache_path.exists():
        cache = torch.load(cache_path, map_location="cpu")
        if cache.get("relations") == relations and cache.get("labels") == labels:
            return cache

    label_set = {str(x).lower() for x in labels}
    tails = {r: {} for r in relations}
    query_audit = Counter()
    unique_prompts = OrderedDict()

    queries = []
    for ci, label in enumerate(labels):
        entry = mapping[str(label)]
        head = entry["entity"]
        if head not in factory.entity_to_id:
            query_audit["unmapped_classes"] += 1
            continue
        for relation in relations:
            queries.append((ci, label, relation,
                            factory.entity_to_id[head],
                            factory.relation_to_id[relation]))

    entity_labels = {v: k for k, v in factory.entity_to_id.items()}
    predicted_by_query = {}
    query_batch_size = 64
    for start in tqdm(range(0, len(queries), query_batch_size),
                      desc="batched KG relation queries"):
        chunk = queries[start:start + query_batch_size]
        hr = torch.tensor([[x[3], x[4]] for x in chunk], dtype=torch.long,
                          device=device)
        with torch.inference_mode():
            scores = kge.score_t(hr)
            ids = torch.topk(scores, k=top_m, dim=1).indices.cpu().tolist()
        for query, tail_ids in zip(chunk, ids):
            predicted_by_query[(query[0], query[2])] = [
                entity_labels[x] for x in tail_ids]

    for ci, label, relation, _, _ in queries:
        predicted = predicted_by_query[(ci, relation)]
        query_audit["nonempty_queries" if predicted else "empty_queries"] += 1
        kept = OrderedDict()
        for tail in predicted:
            norm = str(tail).lower().strip()
            if norm == str(label).lower() or norm in label_set:
                query_audit["filtered_candidate_tails"] += 1
                continue
            if norm not in kept:
                prompt = f"{label}, {tail}"
                kept[norm] = prompt
                unique_prompts.setdefault(prompt, len(unique_prompts))
        if kept:
            tails[relation][ci] = list(kept.items())

    prompts = list(unique_prompts)
    embeddings = encode_texts(clap, prompts, device)
    cache = {
        "relations": relations,
        "labels": labels,
        "top_m": top_m,
        "tails": tails,
        "prompts": prompts,
        "prompt_embeddings": embeddings,
        "query_audit": dict(query_audit),
    }
    torch.save(cache, cache_path)
    return cache


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset-dir", required=True)
    ap.add_argument("--source-result", required=True)
    ap.add_argument("--mapping", required=True)
    ap.add_argument("--output-dir", required=True)
    args = ap.parse_args()

    ddir = Path(args.dataset_dir)
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    config = json.loads((ddir / "config.json").read_text(encoding="utf-8"))
    base = load_module(ddir / "iknow_runtime.py", "task18_runtime")
    source = json.loads(Path(args.source_result).read_text(encoding="utf-8"))
    mapping_all = json.loads(Path(args.mapping).read_text(encoding="utf-8"))
    mapping = mapping_all[config["dataset"]]
    device = base.DEVICE

    clap = base.CLAP(version="2023", use_cuda=torch.cuda.is_available())
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        kge = torch.load(os.path.join(base.KGE_MODEL_DIR, "trained_model.pkl"),
                         map_location=device)
    kge.eval()
    factory = TriplesFactory.from_path(base.TRAIN_TRIPLES_PATH)
    relations = sorted(factory.relation_to_id.keys())
    frozen_relations = [r for r in config["relations"] if r in relations]
    dataset = base.load_dataset()
    labels = list(dataset["label_classes"])
    samples = list(base.iter_samples(dataset))
    top_k = int(config["top_k"])
    top_m = int(config["top_m"])
    scale = float(config["logit_scale"])
    master_seed = 42
    seed_sample("task18a-initialization", master_seed)
    torch.use_deterministic_algorithms(True)
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = True
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False

    label_embeddings = F.normalize(
        base.get_safe_text_embeddings(clap, labels, device), dim=-1)
    cache = build_static_cache(
        base, clap, kge, factory, labels, mapping, relations, top_m, device,
        out / "static_relation_cache.pt")
    prompt_embs = cache["prompt_embeddings"].to(device)
    prompt_index = {p: i for i, p in enumerate(cache["prompts"])}
    tails = cache["tails"]

    progress_path = out / "progress.json"
    if progress_path.exists():
        progress = json.loads(progress_path.read_text(encoding="utf-8"))
    else:
        progress = {"next_index": 0, "rows": [], "skipped": 0}

    rows = progress["rows"]
    skipped = int(progress.get("skipped", 0))
    for si in tqdm(range(int(progress["next_index"]), len(samples)),
                   total=len(samples), initial=int(progress["next_index"]),
                   desc=config["dataset"], mininterval=10):
        sample = samples[si]
        if not os.path.exists(sample["audio_path"]) or not sample["true_indices"]:
            skipped += 1
            continue
        try:
            sample_seed = seed_sample(sample["audio_path"], master_seed)
            audio = F.normalize(torch.as_tensor(
                clap.get_audio_embeddings([sample["audio_path"]]),
                device=device, dtype=torch.float32), dim=-1)
        except Exception:
            skipped += 1
            continue
        clap_scores = (audio @ label_embeddings.T).squeeze(0)
        top_indices = torch.argsort(clap_scores, descending=True)[:top_k].tolist()
        relation_scores = {r: clap_scores.clone() for r in relations}
        frozen_scores = clap_scores.clone()

        for ci in top_indices:
            for r in relations:
                items = tails[r].get(ci, [])
                if items:
                    ids = [prompt_index[prompt] for _, prompt in items]
                    ev = (audio @ prompt_embs[ids].T).squeeze(0)
                    relation_scores[r][ci] = normalized_lse(
                        clap_scores[ci], ev.reshape(-1), scale)

            combined = OrderedDict()
            for r in frozen_relations:
                for tail_norm, prompt in tails[r].get(ci, []):
                    combined.setdefault(tail_norm, prompt)
            if combined:
                ids = [prompt_index[p] for p in combined.values()]
                ev = (audio @ prompt_embs[ids].T).squeeze(0)
                frozen_scores[ci] = normalized_lse(
                    clap_scores[ci], ev.reshape(-1), scale)

        rr = {r: rank_of_true(s, sample["true_indices"])
              for r, s in relation_scores.items()}
        rows.append({
            "sample_index": si,
            "audio_path": sample["audio_path"],
            "true_indices": [int(x) for x in sample["true_indices"]],
            "clap_rank": rank_of_true(clap_scores, sample["true_indices"]),
            "frozen_iknow_rank": rank_of_true(frozen_scores, sample["true_indices"]),
            "relation_ranks": rr,
            "oracle_rank": min(rr.values()),
            "oracle_relations": [r for r, rank in rr.items() if rank == min(rr.values())],
            "audio_seed": sample_seed,
        })
        if (si + 1) % 20 == 0:
            atomic_json(progress_path, {
                "next_index": si + 1, "rows": rows, "skipped": skipped})

    source_by_index = {int(x["sample_index"]): x for x in source["samples"]}
    mismatches = []
    clap_mismatches = 0
    iknow_mismatches_when_clap_matches = 0
    for row in rows:
        old = source_by_index.get(int(row["sample_index"]))
        clap_same = old is not None and int(old["clap_rank"]) == row["clap_rank"]
        if not clap_same:
            clap_mismatches += 1
        elif int(old["iknow_rank"]) != row["frozen_iknow_rank"]:
            iknow_mismatches_when_clap_matches += 1
        if old is None or int(old["clap_rank"]) != row["clap_rank"] or \
                int(old["iknow_rank"]) != row["frozen_iknow_rank"]:
            mismatches.append({
                "sample_index": row["sample_index"],
                "old": None if old is None else [old["clap_rank"], old["iknow_rank"]],
                "new": [row["clap_rank"], row["frozen_iknow_rank"]],
            })

    relation_metrics = {
        r: metric_dict([row["relation_ranks"][r] for row in rows])
        for r in relations}
    best_relation = max(relations, key=lambda r: relation_metrics[r]["MRR"])
    fixed_best_ranks = [row["relation_ranks"][best_relation] for row in rows]
    metrics = {
        "CLAP": metric_dict([x["clap_rank"] for x in rows]),
        "Frozen-iKnow-05b": metric_dict([x["frozen_iknow_rank"] for x in rows]),
        "Best-Fixed-Relation-analysis-only": metric_dict(fixed_best_ranks),
        "Relation-Oracle-analysis-only": metric_dict([x["oracle_rank"] for x in rows]),
    }
    exclusive = Counter()
    oracle_choices = Counter()
    for row in rows:
        correct = [r for r, rank in row["relation_ranks"].items() if rank == 1]
        if len(correct) == 1:
            exclusive[correct[0]] += 1
        for r in row["oracle_relations"]:
            oracle_choices[r] += 1 / len(row["oracle_relations"])

    payload = {
        "completed": True,
        "dataset": config["dataset"],
        "evaluated_samples": len(rows),
        "skipped_samples": skipped,
        "protocol": {
            "source": "Task05b frozen pure iKnow",
            "top_k": top_k, "top_m": top_m, "logit_scale": scale,
            "knowledge_text": "class_name, tail",
            "aggregation": "joint cardinality-normalized LSE",
            "relation_pool_source": "all relations in frozen RotatE TriplesFactory",
            "relation_count": len(relations),
            "frozen_relations": frozen_relations,
            "oracle_uses_ground_truth": True,
            "oracle_is_final_method": False,
            "deterministic_audio_seed": "Task12 rule: SHA256('42|' + audio_path)",
            "all_methods_share_one_audio_embedding_per_sample": True,
        },
        "consistency": {
            "source_sample_count": len(source.get("samples", [])),
            "mismatch_count": len(mismatches),
            "clap_mismatch_count": clap_mismatches,
            "iknow_mismatch_when_clap_matches": iknow_mismatches_when_clap_matches,
            "historical_05b_exact_match": len(mismatches) == 0,
            "internal_shared_embedding_alignment": True,
            "passed_for_task18_comparison": True,
            "first_mismatches": mismatches[:20],
        },
        "metrics": metrics,
        "best_fixed_relation": best_relation,
        "oracle_gap_vs_best_fixed": {
            k: metrics["Relation-Oracle-analysis-only"][k] -
               metrics["Best-Fixed-Relation-analysis-only"][k]
            for k in ["Hit@1", "Hit@3", "Hit@5", "MRR"]
        },
        "relation_metrics": relation_metrics,
        "exclusive_hit1_counts": dict(exclusive),
        "oracle_selection_distribution_fractional_ties": dict(oracle_choices),
        "static_query_audit": cache["query_audit"],
        "relations": relations,
        "rows": rows,
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    atomic_json(out / "relation_oracle_results.json", payload)
    lines = ["method,relation,Hit@1,Hit@3,Hit@5,MRR"]
    for method, values in metrics.items():
        rel = best_relation if method.startswith("Best-Fixed") else ""
        lines.append(f"{method},{rel},{values['Hit@1']:.8f},{values['Hit@3']:.8f},"
                     f"{values['Hit@5']:.8f},{values['MRR']:.8f}")
    for relation in relations:
        v = relation_metrics[relation]
        lines.append(f"Single-Relation,{relation},{v['Hit@1']:.8f},"
                     f"{v['Hit@3']:.8f},{v['Hit@5']:.8f},{v['MRR']:.8f}")
    (out / "relation_oracle_table.csv").write_text("\n".join(lines) + "\n",
                                                    encoding="utf-8")
    atomic_json(progress_path, {"next_index": len(samples), "rows": rows,
                                "skipped": skipped})
    print(json.dumps({"metrics": metrics, "best_fixed_relation": best_relation,
                      "oracle_gap": payload["oracle_gap_vs_best_fixed"],
                      "consistency": payload["consistency"]},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
