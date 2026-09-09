#!/usr/bin/env python3
"""One-hop verbalization audit on the corrected strict-map K5/M3 baseline."""

import hashlib
import importlib.util
import json
import math
import os
import time
import warnings
from collections import OrderedDict, Counter
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from pykeen.triples import TriplesFactory
from tqdm import tqdm

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CONFIG = json.loads((HERE / "config.json").read_text(encoding="utf-8"))
MAPPING_FILE = ROOT / "entity_mapping_v2.json"
RUNTIME = HERE / "iknow_runtime.py"
RESULTS = HERE / "results"
CACHE = HERE / "cache"
RESULT_FILE = RESULTS / "onehop_text_audit_results.json"
TABLE_FILE = RESULTS / "onehop_text_audit_table.csv"
PROGRESS_FILE = RESULTS / "progress.json"

TOP_K = 5
TOP_M = 3
FUSION_TOP_P = 5
ALPHA_MIN = 0.4
ALPHA_MAX = 0.8


def load_runtime():
    spec = importlib.util.spec_from_file_location("strict_runtime", str(RUNTIME))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def metrics(ranks):
    values = np.asarray(ranks, dtype=np.float64)
    return {
        "Hit@1": float(100 * np.mean(values <= 1)),
        "Hit@3": float(100 * np.mean(values <= 3)),
        "Hit@5": float(100 * np.mean(values <= 5)),
        "MRR": float(100 * np.mean(1.0 / values)),
    }


def rank_of_true(scores, true_indices):
    order = torch.argsort(scores, descending=True).detach().cpu().tolist()
    return min(order.index(int(target)) + 1 for target in true_indices)


def normalized_lse(values, scale):
    return (torch.logsumexp(scale * values, dim=0) - math.log(values.numel())) / scale


def joint_lse(base_score, evidence_scores, scale):
    return normalized_lse(torch.cat([base_score.reshape(1), evidence_scores]), scale)


def dynamic_alpha(base_scores):
    confidence = float(torch.max(base_scores))
    return float(np.clip(ALPHA_MIN + (ALPHA_MAX - ALPHA_MIN) * confidence,
                         ALPHA_MIN, ALPHA_MAX))


def ours_fusion(base_score, evidence_scores, alpha, scale):
    if evidence_scores.numel() == 0:
        return base_score
    keep = torch.argsort(evidence_scores, descending=True, stable=True)[:FUSION_TOP_P]
    pooled = normalized_lse(evidence_scores[keep], scale)
    return alpha * base_score + (1.0 - alpha) * pooled


def indefinite_article(text):
    return "an" if str(text).strip().lower()[:1] in "aeiou" else "a"


def template_sentence(head, relation, tail):
    """Frozen deterministic templates reconstructed from the old template files."""
    a = indefinite_article(head)
    b = indefinite_article(tail)
    templates = {
        "belongs to class": f"The sound of {head} belongs to the broader class of {tail}.",
        "has parent": f"The acoustic category of {head} has a parent category of {tail}.",
        "perceived as": f"The sound of {head} is often perceived as {tail}.",
        "event composed of": f"The sound of {head} is characterized by {tail}.",
        "has children": f"The sound of {head} includes subtypes such as {tail}.",
        "overlaps with": f"The sound of {head} often overlaps with {tail}.",
        "occurs in": f"{a.capitalize()} {head} typically occurs in {b} {tail}.",
        "associated with environment": f"The sound of {a} {head} is heavily associated with {b} {tail} environment.",
        "localized in": f"{a.capitalize()} {head} is usually localized in {b} {tail}.",
        "used for": f"{a.capitalize()} {head} is generally used for {tail}.",
        "part of scene": f"The sound of {a} {head} is a common part of {b} {tail} scene.",
        "is sound of": f"The sound of {head} is characteristic of {tail}.",
        "transcribed as": f"The sound of {head} is transcribed as {tail}.",
        "indicates": f"The sound of {a} {head} typically indicates {tail}.",
        "described by": f"The sound of {a} {head} can be described by {tail}.",
        "is instance of": f"{a.capitalize()} {head} is a specific instance of {tail}.",
        "is a type of": f"The sound of {head} is a type of {tail}.",
        "is variant of": f"The sound of {head} is a variant of {tail}.",
        "scene contains": f"A scene of {head} commonly contains the sound of {tail}.",
    }
    return templates.get(relation, f"The sound of {head} is related to {tail}.")


def build_or_load_cache(base, clap, kge, factory, dataset, device):
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / "onehop_text_cache.pt"
    labels = list(dataset["label_classes"])
    kg_classes = list(dataset["kg_classes"])
    mapping_all = json.loads(MAPPING_FILE.read_text(encoding="utf-8"))
    mapping = mapping_all[CONFIG["dataset"]]
    signature = {
        "dataset": CONFIG["dataset"], "labels": labels, "kg_classes": kg_classes,
        "mapping_sha256": sha256(MAPPING_FILE), "relations": CONFIG["relations"],
        "top_k": TOP_K, "top_m": TOP_M, "forms": ["direct", "raw_triple", "template_v1"],
    }
    sig = hashlib.sha256(json.dumps(signature, sort_keys=True).encode()).hexdigest()
    if path.exists():
        saved = torch.load(path, map_location="cpu")
        if saved.get("signature_hash") == sig:
            return saved, saved["label_embeddings"].to(device), saved["evidence_embeddings"].to(device)

    base.TOP_M = TOP_M
    get_tails = base.build_tail_predictor(kge, factory)
    valid_relations = [r for r in CONFIG["relations"] if r in factory.relation_to_id]
    candidate_labels = {str(x).lower().strip() for x in labels}
    all_texts, text_to_id, class_index = [], {}, []
    audit = Counter(mapped_classes=0, unmapped_classes=0, queries=0, empty_queries=0,
                    candidate_tail_removed=0, duplicate_tail_removed=0, triples=0)

    def text_id(text):
        if text not in text_to_id:
            text_to_id[text] = len(all_texts); all_texts.append(text)
        return text_to_id[text]

    for class_name, kg_class in zip(labels, kg_classes):
        entry = mapping[str(class_name)]
        entity = entry.get("entity")
        triples = OrderedDict()
        if not entity or entity not in factory.entity_to_id:
            audit["unmapped_classes"] += 1
        else:
            audit["mapped_classes"] += 1
            for relation in valid_relations:
                tails = get_tails(entity, relation); audit["queries"] += 1
                if not tails: audit["empty_queries"] += 1
                for tail in tails:
                    norm = str(tail).lower().strip()
                    if norm == str(class_name).lower().strip() or norm in candidate_labels:
                        audit["candidate_tail_removed"] += 1; continue
                    if norm in triples:
                        audit["duplicate_tail_removed"] += 1; continue
                    triples[norm] = (relation, str(tail))
        audit["triples"] += len(triples)
        ids = {"direct": [], "raw": [], "template": []}
        triple_rows = []
        for relation, tail in triples.values():
            direct = f"{class_name}, {tail}"
            raw = f"{class_name} {relation} {tail}"
            template = template_sentence(class_name, relation, tail)
            ids["direct"].append(text_id(direct)); ids["raw"].append(text_id(raw)); ids["template"].append(text_id(template))
            triple_rows.append({"head": class_name, "kg_entity": entity, "relation": relation, "tail": tail,
                                "direct": direct, "raw": raw, "template": template})
        class_index.append({"ids": ids, "triples": triple_rows, "mapped_entity": entity})

    label_embeddings = F.normalize(base.get_safe_text_embeddings(clap, labels, device), dim=-1)
    chunks = []
    for start in range(0, len(all_texts), 128):
        chunks.append(F.normalize(base.get_safe_text_embeddings(clap, all_texts[start:start + 128], device), dim=-1))
    evidence_embeddings = torch.cat(chunks) if chunks else torch.empty((0, label_embeddings.shape[1]), device=device)
    saved = {"signature": signature, "signature_hash": sig, "label_embeddings": label_embeddings.cpu(),
             "evidence_embeddings": evidence_embeddings.cpu(), "texts": all_texts,
             "class_index": class_index, "audit": dict(audit)}
    torch.save(saved, path)
    (CACHE / "triples_and_texts.json").write_text(json.dumps({"signature": signature, "audit": dict(audit),
                                                               "classes": class_index}, ensure_ascii=False, indent=2), encoding="utf-8")
    return saved, label_embeddings, evidence_embeddings


def save_progress(next_index, ranks, rows):
    RESULTS.mkdir(parents=True, exist_ok=True)
    temp = PROGRESS_FILE.with_suffix(".tmp")
    temp.write_text(json.dumps({"next_index": next_index, "ranks": ranks, "samples": rows}, ensure_ascii=False), encoding="utf-8")
    os.replace(temp, PROGRESS_FILE)


@torch.no_grad()
def main():
    RESULTS.mkdir(parents=True, exist_ok=True)
    base = load_runtime(); device = base.DEVICE
    print("Starting strict one-hop text audit: " + CONFIG["dataset"], flush=True)
    clap = base.CLAP(version="2023", use_cuda=torch.cuda.is_available())
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        kge = torch.load(os.path.join(base.KGE_MODEL_DIR, "trained_model.pkl"), map_location=device)
    kge.eval(); factory = TriplesFactory.from_path(base.TRAIN_TRIPLES_PATH)
    dataset = base.load_dataset(); samples = list(base.iter_samples(dataset))
    cache, label_emb, evidence_emb = build_or_load_cache(base, clap, kge, factory, dataset, device)
    forms = ["direct", "raw", "template"]
    methods = ["CLAP", "iKnow-1st", "Ours1-Direct", "Ours1-RawTriple", "Ours1-Template", "Ours1-Oracle"]
    ranks = {m: [] for m in methods}; rows = []; scale = float(CONFIG["logit_scale"])

    for sample_index, sample in enumerate(tqdm(samples, desc=CONFIG["dataset"], mininterval=10)):
        if not os.path.exists(sample["audio_path"]) or not sample["true_indices"]: continue
        try:
            audio = F.normalize(base.to_tensor(clap.get_audio_embeddings([sample["audio_path"]])).to(device).float(), dim=-1)
        except Exception:
            continue
        base_scores = torch.matmul(audio, label_emb.T).squeeze(0)
        evidence_scores = torch.matmul(audio, evidence_emb.T).squeeze(0)
        top_indices = torch.argsort(base_scores, descending=True)[:TOP_K].tolist()
        alpha = dynamic_alpha(base_scores)
        vectors = {m: base_scores.clone() for m in methods if m != "Ours1-Oracle"}
        for class_id in top_indices:
            ids = cache["class_index"][class_id]["ids"]
            direct_scores = evidence_scores[ids["direct"]] if ids["direct"] else torch.empty(0, device=device)
            if direct_scores.numel(): vectors["iKnow-1st"][class_id] = joint_lse(base_scores[class_id], direct_scores, scale)
            for form, method in zip(forms, ["Ours1-Direct", "Ours1-RawTriple", "Ours1-Template"]):
                scores = evidence_scores[ids[form]] if ids[form] else torch.empty(0, device=device)
                vectors[method][class_id] = ours_fusion(base_scores[class_id], scores, alpha, scale)
        sample_ranks = {m: rank_of_true(v, sample["true_indices"]) for m, v in vectors.items()}
        oracle_rank = min(sample_ranks[m] for m in ["Ours1-Direct", "Ours1-RawTriple", "Ours1-Template"])
        sample_ranks["Ours1-Oracle"] = oracle_rank
        for m in methods: ranks[m].append(int(sample_ranks[m]))
        rows.append({"sample_index": sample_index, "audio_path": sample["audio_path"],
                     "true_indices": [int(x) for x in sample["true_indices"]], "alpha": alpha,
                     "topk": top_indices, "ranks": sample_ranks})
        if len(rows) % 20 == 0: save_progress(sample_index + 1, ranks, rows)

    table = {m: metrics(ranks[m]) for m in methods}
    best_fixed_h1 = max(table[m]["Hit@1"] for m in ["Ours1-Direct", "Ours1-RawTriple", "Ours1-Template"])
    best_fixed_mrr = max(table[m]["MRR"] for m in ["Ours1-Direct", "Ours1-RawTriple", "Ours1-Template"])
    patterns = Counter()
    for row in rows:
        correct = tuple(name for name, method in [("D", "Ours1-Direct"), ("R", "Ours1-RawTriple"), ("T", "Ours1-Template")]
                        if row["ranks"][method] == 1)
        patterns["+".join(correct) if correct else "None"] += 1
    payload = {"completed": True, "protocol": {"strict_mapping": True, "mapping_sha256": sha256(MAPPING_FILE),
               "top_k": TOP_K, "top_m": TOP_M, "relations": CONFIG["relations"], "hop": 1,
               "only_changed_variable": "verbalization", "fusion_top_p": FUSION_TOP_P,
               "oracle_uses_ground_truth_for_analysis_only": True}, "metrics": table,
               "oracle_gap": {"Hit@1": table["Ours1-Oracle"]["Hit@1"] - best_fixed_h1,
                              "MRR": table["Ours1-Oracle"]["MRR"] - best_fixed_mrr},
               "correctness_patterns": dict(patterns), "cache_audit": cache["audit"], "samples": rows,
               "created_at": time.strftime("%Y-%m-%d %H:%M:%S")}
    RESULT_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = ["method,Hit@1,Hit@3,Hit@5,MRR"]
    for m in methods:
        x = table[m]; lines.append(f"{m},{x['Hit@1']:.8f},{x['Hit@3']:.8f},{x['Hit@5']:.8f},{x['MRR']:.8f}")
    TABLE_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")
    save_progress(len(samples), ranks, rows)
    print(json.dumps({"metrics": table, "oracle_gap": payload["oracle_gap"]}, indent=2), flush=True)


if __name__ == "__main__":
    main()
