#!/usr/bin/env python3
"""Task 18B: label-free sample-level one-hop relation selection."""
import os
os.environ["CUBLAS_WORKSPACE_CONFIG"] = ":4096:8"
os.environ["PYTHONHASHSEED"] = "42"

import argparse, hashlib, importlib.util, json, random, time, warnings
from collections import Counter, OrderedDict
from pathlib import Path
import numpy as np
import torch
import torch.nn.functional as F
from pykeen.triples import TriplesFactory
from tqdm import tqdm


METHODS = ["CLAP", "Frozen-iKnow", "All-47", "Abs-Top1", "Abs-Top3",
           "Gain-Top1", "Gain-Top3", "Relation-Oracle-analysis-only"]


def module(path, name):
    s = importlib.util.spec_from_file_location(name, str(path))
    m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m


def seed_audio(path):
    z = int(hashlib.sha256(("42|" + path).encode()).hexdigest()[:8], 16)
    random.seed(z); np.random.seed(z % (2**32 - 1)); torch.manual_seed(z)
    if torch.cuda.is_available(): torch.cuda.manual_seed_all(z)
    return z


def nlse(base_score, evidence_scores, scale):
    z = torch.cat([base_score.reshape(1) * scale, evidence_scores * scale])
    return (torch.logsumexp(z, 0) - np.log(z.numel())) / scale


def evidence_nlse(scores, scale):
    return (torch.logsumexp(scores * scale, 0) - np.log(scores.numel())) / scale


def rank(scores, truth):
    order = torch.argsort(scores, descending=True).detach().cpu().numpy()
    return min(int(np.where(order == i)[0][0]) + 1 for i in truth)


def metrics(ranks):
    x = np.asarray(ranks, dtype=float)
    return {"Hit@1": float(np.mean(x <= 1) * 100),
            "Hit@3": float(np.mean(x <= 3) * 100),
            "Hit@5": float(np.mean(x <= 5) * 100),
            "MRR": float(np.mean(1 / x) * 100)}


def save(path, obj):
    path = Path(path); tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, path)


def apply_relations(base_scores, per_class, selected, scale):
    out = base_scores.clone()
    for ci, relation_data in per_class.items():
        merged = OrderedDict()
        for r in selected:
            for tail, score in relation_data.get(r, []):
                merged.setdefault(tail, score)
        if merged:
            ev = torch.stack(list(merged.values()))
            out[ci] = nlse(base_scores[ci], ev, scale)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset-dir", required=True)
    ap.add_argument("--task18a-result", required=True)
    ap.add_argument("--task18a-cache", required=True)
    ap.add_argument("--output-dir", required=True)
    a = ap.parse_args()
    ddir, out = Path(a.dataset_dir), Path(a.output_dir); out.mkdir(parents=True, exist_ok=True)
    cfg = json.loads((ddir / "config.json").read_text())
    base = module(ddir / "iknow_runtime.py", "task18b_runtime")
    audit18a = json.loads(Path(a.task18a_result).read_text())
    oracle_by_i = {int(x["sample_index"]): int(x["oracle_rank"])
                   for x in audit18a["rows"]}
    cache = torch.load(a.task18a_cache, map_location="cpu")
    relations, tails = cache["relations"], cache["tails"]

    seed_audio("task18b-initialization")
    torch.use_deterministic_algorithms(True)
    torch.backends.cudnn.benchmark = False; torch.backends.cudnn.deterministic = True
    torch.backends.cuda.matmul.allow_tf32 = False; torch.backends.cudnn.allow_tf32 = False
    device = base.DEVICE
    clap = base.CLAP(version="2023", use_cuda=torch.cuda.is_available())
    data = base.load_dataset(); labels = list(data["label_classes"]); samples = list(base.iter_samples(data))
    label_emb = F.normalize(base.get_safe_text_embeddings(clap, labels, device), dim=-1)
    prompt_emb = cache["prompt_embeddings"].to(device)
    prompt_index = {p: i for i, p in enumerate(cache["prompts"])}
    frozen = [r for r in cfg["relations"] if r in relations]
    topk, scale = int(cfg["top_k"]), float(cfg["logit_scale"])

    prog = out / "progress.json"
    state = json.loads(prog.read_text()) if prog.exists() else {"next": 0, "rows": []}
    rows = state["rows"]
    selection_counts = {m: Counter() for m in ["Abs-Top1", "Abs-Top3", "Gain-Top1", "Gain-Top3"]}
    for old in rows:
        for m, selected in old.get("selected_relations", {}).items(): selection_counts[m].update(selected)

    for si in tqdm(range(int(state["next"]), len(samples)), total=len(samples),
                   initial=int(state["next"]), desc=cfg["dataset"], mininterval=10):
        s = samples[si]
        if not os.path.exists(s["audio_path"]) or not s["true_indices"]:
            raise RuntimeError(f"invalid frozen sample {si}: {s['audio_path']}")
        sample_seed = seed_audio(s["audio_path"])
        audio = F.normalize(base.to_tensor(clap.get_audio_embeddings([s["audio_path"]])).to(device).float(), dim=-1)
        clap_scores = (audio @ label_emb.T).squeeze(0)
        top = torch.argsort(clap_scores, descending=True)[:topk].tolist()
        per_class = {}
        abs_values = {r: [] for r in relations}; gain_values = {r: [] for r in relations}
        for ci in top:
            per_class[ci] = {}
            for r in relations:
                items = tails[r].get(ci, [])
                if not items:
                    abs_values[r].append(-1.0); gain_values[r].append(-1.0); continue
                ids = [prompt_index[p] for _, p in items]
                ev = (audio @ prompt_emb[ids].T).reshape(-1)
                per_class[ci][r] = [(tail, score) for (tail, _), score in zip(items, ev)]
                q = float(evidence_nlse(ev, scale).item())
                abs_values[r].append(q); gain_values[r].append(q - float(clap_scores[ci].item()))
        q_abs = {r: float(np.mean(v)) for r, v in abs_values.items()}
        q_gain = {r: float(np.mean(v)) for r, v in gain_values.items()}
        abs_order = sorted(relations, key=lambda r: (-q_abs[r], r))
        gain_order = sorted(relations, key=lambda r: (-q_gain[r], r))
        selected = {"Abs-Top1": abs_order[:1], "Abs-Top3": abs_order[:3],
                    "Gain-Top1": gain_order[:1], "Gain-Top3": gain_order[:3]}
        for m, rs in selected.items(): selection_counts[m].update(rs)
        scores = {"CLAP": clap_scores,
                  "Frozen-iKnow": apply_relations(clap_scores, per_class, frozen, scale),
                  "All-47": apply_relations(clap_scores, per_class, relations, scale)}
        for m, rs in selected.items(): scores[m] = apply_relations(clap_scores, per_class, rs, scale)
        ranks = {m: rank(v, s["true_indices"]) for m, v in scores.items()}
        ranks["Relation-Oracle-analysis-only"] = oracle_by_i[si]
        rows.append({"sample_index": si, "audio_path": s["audio_path"],
                     "true_indices": [int(x) for x in s["true_indices"]],
                     "audio_seed": sample_seed, "selected_relations": selected,
                     "selection_scores": {"absolute": q_abs, "gain": q_gain}, "ranks": ranks})
        if (si + 1) % 20 == 0: save(prog, {"next": si + 1, "rows": rows})

    met = {m: metrics([x["ranks"][m] for x in rows]) for m in METHODS}
    payload = {"completed": True, "dataset": cfg["dataset"], "n": len(rows),
               "protocol": {"base": "Task05b one-hop", "seed": "Task12 SHA256 path rule",
                            "top_k": topk, "top_m": cfg["top_m"], "scale": scale,
                            "text": "class_name, tail", "hop": 1,
                            "selector_uses_labels": False,
                            "missing_relation_candidate_utility": -1.0,
                            "absolute": "mean evidence-only normalized LSE over CLAP Top-K classes",
                            "gain": "absolute utility minus base class similarity",
                            "final_aggregation": "frozen joint cardinality-normalized LSE"},
               "metrics": met,
               "selection_counts": {m: dict(c) for m, c in selection_counts.items()},
               "rows": rows, "created_at": time.strftime("%F %T")}
    save(out / "selector_results.json", payload)
    lines = ["method,Hit@1,Hit@3,Hit@5,MRR"] + [
        f"{m},{met[m]['Hit@1']:.8f},{met[m]['Hit@3']:.8f},{met[m]['Hit@5']:.8f},{met[m]['MRR']:.8f}"
        for m in METHODS]
    (out / "selector_table.csv").write_text("\n".join(lines) + "\n")
    save(prog, {"next": len(samples), "rows": rows})
    print(json.dumps(met, indent=2))

if __name__ == "__main__": main()
