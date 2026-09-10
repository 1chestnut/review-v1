#!/usr/bin/env python3
"""Task 08: label-free sample router over the three frozen Task-06 verbalizations."""

import importlib.util
import json
import math
import os
import time
import warnings
from collections import Counter
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from pykeen.triples import TriplesFactory
from tqdm import tqdm

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CONFIG = json.loads((HERE / "config.json").read_text(encoding="utf-8"))
RUNTIME = HERE / "iknow_runtime.py"
TASK06_CACHE = Path(CONFIG["task06_cache"])
RESULTS = HERE / "results"
RESULT_JSON = RESULTS / "unlabeled_router_results.json"
RESULT_CSV = RESULTS / "unlabeled_router_table.csv"
SCORES_NPZ = RESULTS / "class_scores_float16.npz"
PROGRESS = RESULTS / "progress.json"

TOP_K = 5
FUSION_TOP_P = 5
ALPHA_MIN = 0.4
ALPHA_MAX = 0.8
EXPERTS = ["Direct", "RawTriple", "Template"]


def load_runtime():
    spec = importlib.util.spec_from_file_location("strict_runtime", str(RUNTIME))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def metrics(ranks):
    a = np.asarray(ranks, dtype=np.float64)
    return {"Hit@1": float(100*np.mean(a <= 1)), "Hit@3": float(100*np.mean(a <= 3)),
            "Hit@5": float(100*np.mean(a <= 5)), "MRR": float(100*np.mean(1/a))}


def rank_of_true(scores, true_indices):
    order = torch.argsort(scores, descending=True).detach().cpu().tolist()
    return min(order.index(int(i)) + 1 for i in true_indices)


def normalized_lse(values, scale):
    return (torch.logsumexp(scale * values, dim=0) - math.log(values.numel())) / scale


def dynamic_alpha(base_scores):
    confidence = float(torch.max(base_scores))
    return float(np.clip(ALPHA_MIN + (ALPHA_MAX-ALPHA_MIN)*confidence, ALPHA_MIN, ALPHA_MAX))


def ours_fusion(base_score, evidence_scores, alpha, scale):
    if evidence_scores.numel() == 0:
        return base_score
    keep = torch.argsort(evidence_scores, descending=True, stable=True)[:FUSION_TOP_P]
    pooled = normalized_lse(evidence_scores[keep], scale)
    return alpha*base_score + (1-alpha)*pooled


def selector_stats(scores, scale):
    """Return label-free entropy and probability-margin diagnostics."""
    probs = torch.softmax(scale * scores, dim=0)
    entropy = float(-(probs * torch.log(probs.clamp_min(1e-12))).sum())
    top2 = torch.topk(probs, k=min(2, probs.numel())).values
    margin = float(top2[0] - top2[1]) if top2.numel() > 1 else float(top2[0])
    return entropy, margin


def save_progress(next_index, ranks, rows):
    RESULTS.mkdir(parents=True, exist_ok=True)
    tmp = PROGRESS.with_suffix(".tmp")
    tmp.write_text(json.dumps({"next_index": next_index, "ranks": ranks, "samples": rows},
                              ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, PROGRESS)


@torch.no_grad()
def main():
    RESULTS.mkdir(parents=True, exist_ok=True)
    base = load_runtime(); device = base.DEVICE
    print("Starting Task08 unlabeled router: " + CONFIG["dataset"], flush=True)
    clap = base.CLAP(version="2023", use_cuda=torch.cuda.is_available())
    # Loaded only because the frozen dataset runtime imports/uses the same environment.
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        kge = torch.load(os.path.join(base.KGE_MODEL_DIR, "trained_model.pkl"), map_location=device)
    kge.eval(); TriplesFactory.from_path(base.TRAIN_TRIPLES_PATH)
    dataset = base.load_dataset(); samples = list(base.iter_samples(dataset))

    cache = torch.load(TASK06_CACHE / "onehop_text_cache.pt", map_location="cpu")
    label_emb = cache["label_embeddings"].to(device)
    evidence_emb = cache["evidence_embeddings"].to(device)
    forms = ["direct", "raw", "template"]
    methods = ["All-Direct", "All-RawTriple", "All-Template",
               "Entropy-Router", "Margin-Router", "Oracle"]
    ranks = {m: [] for m in methods}; rows = []
    saved_scores = {m: [] for m in EXPERTS}
    selector_counts = {"Entropy-Router": Counter(), "Margin-Router": Counter()}
    oracle_agreement = Counter(); flips = Counter(); scale = float(CONFIG["logit_scale"])

    for sample_index, sample in enumerate(tqdm(samples, desc=CONFIG["dataset"], mininterval=10)):
        if not os.path.exists(sample["audio_path"]) or not sample["true_indices"]:
            continue
        try:
            audio = F.normalize(base.to_tensor(clap.get_audio_embeddings([sample["audio_path"]])).to(device).float(), dim=-1)
        except Exception:
            continue
        base_scores = torch.matmul(audio, label_emb.T).squeeze(0)
        ev_scores = torch.matmul(audio, evidence_emb.T).squeeze(0)
        top_indices = torch.argsort(base_scores, descending=True)[:TOP_K].tolist()
        alpha = dynamic_alpha(base_scores)
        vectors = {name: base_scores.clone() for name in EXPERTS}
        for class_id in top_indices:
            ids = cache["class_index"][class_id]["ids"]
            for form, name in zip(forms, EXPERTS):
                scores = ev_scores[ids[form]] if ids[form] else torch.empty(0, device=device)
                vectors[name][class_id] = ours_fusion(base_scores[class_id], scores, alpha, scale)

        diagnostics = {name: selector_stats(vectors[name], scale) for name in EXPERTS}
        entropy_choice = min(EXPERTS, key=lambda n: (diagnostics[n][0], EXPERTS.index(n)))
        margin_choice = max(EXPERTS, key=lambda n: (diagnostics[n][1], -EXPERTS.index(n)))
        fixed_ranks = {name: rank_of_true(vectors[name], sample["true_indices"]) for name in EXPERTS}
        best_rank = min(fixed_ranks.values())
        oracle_best = [name for name in EXPERTS if fixed_ranks[name] == best_rank]
        method_ranks = {"All-Direct": fixed_ranks["Direct"],
                        "All-RawTriple": fixed_ranks["RawTriple"],
                        "All-Template": fixed_ranks["Template"],
                        "Entropy-Router": fixed_ranks[entropy_choice],
                        "Margin-Router": fixed_ranks[margin_choice],
                        "Oracle": best_rank}
        for m in methods: ranks[m].append(int(method_ranks[m]))
        selector_counts["Entropy-Router"][entropy_choice] += 1
        selector_counts["Margin-Router"][margin_choice] += 1
        oracle_agreement["Entropy-Router"] += int(entropy_choice in oracle_best)
        oracle_agreement["Margin-Router"] += int(margin_choice in oracle_best)
        for router, choice in [("Entropy", entropy_choice), ("Margin", margin_choice)]:
            t_ok = fixed_ranks["Template"] == 1; r_ok = fixed_ranks[choice] == 1
            flips[f"{router}:TemplateWrong_to_RouterCorrect"] += int((not t_ok) and r_ok)
            flips[f"{router}:TemplateCorrect_to_RouterWrong"] += int(t_ok and (not r_ok))
        for name in EXPERTS: saved_scores[name].append(vectors[name].detach().cpu().numpy().astype(np.float16))
        rows.append({"sample_index": sample_index, "audio_path": sample["audio_path"],
                     "true_indices": [int(x) for x in sample["true_indices"]],
                     "entropy_choice": entropy_choice, "margin_choice": margin_choice,
                     "entropy": {n: diagnostics[n][0] for n in EXPERTS},
                     "margin": {n: diagnostics[n][1] for n in EXPERTS}, "ranks": method_ranks})
        if len(rows) % 20 == 0: save_progress(sample_index+1, ranks, rows)

    table = {m: metrics(ranks[m]) for m in methods}; n = len(rows)
    np.savez_compressed(SCORES_NPZ, **{n: np.asarray(v, dtype=np.float16) for n,v in saved_scores.items()})
    payload = {"completed": True,
               "protocol": {"uses_ground_truth_for_router": False, "selection_scope": "per sample",
                            "probability_scale": scale, "entropy_rule": "minimum entropy",
                            "margin_rule": "maximum top1-top2 probability margin",
                            "frozen_from_task06": True, "top_k": TOP_K, "fusion_top_p": FUSION_TOP_P},
               "metrics": table,
               "selection_counts": {k: dict(v) for k,v in selector_counts.items()},
               "oracle_choice_agreement_percent": {k: 100*v/n for k,v in oracle_agreement.items()},
               "template_flip_counts": dict(flips), "samples": rows,
               "score_file": SCORES_NPZ.name, "created_at": time.strftime("%F %T")}
    RESULT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = ["method,Hit@1,Hit@3,Hit@5,MRR"]
    for m in methods:
        x=table[m]; lines.append(f"{m},{x['Hit@1']:.8f},{x['Hit@3']:.8f},{x['Hit@5']:.8f},{x['MRR']:.8f}")
    RESULT_CSV.write_text("\n".join(lines)+"\n", encoding="utf-8")
    save_progress(len(samples), ranks, rows)
    print(json.dumps({"metrics":table,"selection_counts":payload["selection_counts"],
                      "oracle_agreement":payload["oracle_choice_agreement_percent"],
                      "flips":payload["template_flip_counts"]}, indent=2), flush=True)


if __name__ == "__main__":
    main()
