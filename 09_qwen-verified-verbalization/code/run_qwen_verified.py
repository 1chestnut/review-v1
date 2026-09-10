#!/usr/bin/env python3
"""Task 09: change only one-hop triple verbalization from Task 06."""

import argparse
import gc
import hashlib
import importlib.util
import json
import math
import os
import re
import time
import warnings
from collections import Counter
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from pykeen.triples import TriplesFactory
from tqdm import tqdm
from transformers import AutoModelForCausalLM, AutoTokenizer

ROOT = Path("/data/zkx/zkx/review1")
SOURCE_ROOT = ROOT / "06_onehop-text-verbalization-audit"
TASK_ROOT = ROOT / "09_qwen-verified-verbalization"
MODEL_PATH = Path("/data/zkx/zkx/iknow-audio/data/model/千问")

SYSTEM_PROMPT = """You are a faithful knowledge-graph verbalizer.
Convert exactly one knowledge-graph triple into one short, natural English sentence.

Rules:
1. Use only information explicitly contained in the triple.
2. Preserve the head entity, relation meaning, relation direction, and tail entity.
3. Do not add acoustic properties, causes, locations, purposes, examples, explanations, or external knowledge.
4. Do not omit either entity or the relation.
5. Do not correct or reinterpret the factual content, even if it seems unusual.
6. Add only grammatical function words such as articles, prepositions, and forms of "be".
7. Silently verify that the sentence expresses exactly the supplied triple.
8. Output only one final sentence, without reasoning, labels, headers, or quotation marks."""

REPAIR_PROMPT = """Your preceding sentence failed an automatic fidelity check.
Rewrite it as exactly one short English sentence. Copy the meanings of the head, relation, and tail exactly. Do not add, correct, explain, or infer anything. Output only the sentence."""

RELATION_TERMS = {
    "belongs to class": (("belong", "class"),),
    "has parent": (("parent",),),
    "perceived as": (("perceiv",),),
    "event composed of": (("compos",), ("consist",), ("character",)),
    "has children": (("child",), ("subtype",), ("include",)),
    "overlaps with": (("overlap",),),
    "occurs in": (("occur",),),
    "associated with environment": (("associat", "environment"),),
    "localized in": (("localiz",), ("located",)),
    "used for": (("used", "for"),),
    "part of scene": (("part", "scene"),),
    "is sound of": (("sound", "of"),),
    "transcribed as": (("transcrib",),),
    "indicates": (("indicat",),),
    "described by": (("describ",),),
    "is instance of": (("instance",),),
    "is a type of": (("type",),),
    "is variant of": (("variant",),),
    "scene contains": (("scene", "contain"),),
}

FORBIDDEN_CONTENT = {
    "rhythm", "rhythmic", "pitch", "pitched", "timbre", "frequency",
    "frequencies", "transient", "loud", "loudness", "quiet", "high-pitched",
    "low-pitched", "harmonic", "melodic", "resonant", "sharp", "soft",
}


def norm(text):
    text = str(text).lower().replace("_", " ")
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


def content_tokens(text):
    stop = {"a", "an", "the", "of", "to", "and", "or", "in", "on", "with"}
    return [x for x in norm(text).split() if x not in stop]


def entity_covered(entity, sentence):
    tokens = content_tokens(entity)
    sentence_tokens = set(content_tokens(sentence))
    return bool(tokens) and all(t in sentence_tokens for t in tokens)


def relation_covered(relation, sentence):
    s = norm(sentence)
    alternatives = RELATION_TERMS.get(norm(relation), ((norm(relation),),))
    return any(all(term in s for term in terms) for terms in alternatives)


def validate(head, relation, tail, sentence):
    reasons = []
    clean = str(sentence).strip().strip('"').strip("'")
    if not entity_covered(head, clean): reasons.append("head_not_covered")
    if not entity_covered(tail, clean): reasons.append("tail_not_covered")
    if not relation_covered(relation, clean): reasons.append("relation_not_explicit")
    if len(clean.split()) > 30: reasons.append("too_long")
    if "\n" in clean: reasons.append("multiple_lines")
    if clean.count(".") + clean.count("!") + clean.count("?") > 1:
        reasons.append("multiple_sentences")
    present_forbidden = sorted(w for w in FORBIDDEN_CONTENT if w in norm(clean).split())
    if present_forbidden: reasons.append("added_acoustic_terms:" + ",".join(present_forbidden))
    if any(x in clean.lower() for x in ("step-by-step", "description:", "head:", "relation:", "tail:")):
        reasons.append("extra_format")
    return clean, reasons


def model_generate(model, tokenizer, messages):
    prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer([prompt], return_tensors="pt").to(model.device)
    with torch.inference_mode():
        ids = model.generate(**inputs, max_new_tokens=48, do_sample=False,
                             pad_token_id=tokenizer.eos_token_id)
    return tokenizer.decode(ids[0, inputs.input_ids.shape[1]:], skip_special_tokens=True).strip()


def generate_dataset(dataset_dir):
    source = SOURCE_ROOT / dataset_dir
    out_dir = TASK_ROOT / dataset_dir
    prompt_dir = out_dir / "prompts"
    prompt_dir.mkdir(parents=True, exist_ok=True)
    source_data = json.loads((source / "cache/triples_and_texts.json").read_text(encoding="utf-8"))
    triples = []
    for class_id, cls in enumerate(source_data["classes"]):
        for triple_id, row in enumerate(cls["triples"]):
            triples.append({"class_id": class_id, "triple_id": triple_id, **row})

    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, local_files_only=True)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_PATH, torch_dtype=torch.bfloat16, device_map="cuda:0", local_files_only=True
    )
    model.eval()
    rows = []
    for i, row in enumerate(tqdm(triples, desc=f"Qwen {dataset_dir}", mininterval=10)):
        user = f"[head] {row['head']}\n[relation] {row['relation']}\n[tail] {row['tail']}"
        messages = [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": user}]
        raw = model_generate(model, tokenizer, messages)
        raw_clean, raw_reasons = validate(row["head"], row["relation"], row["tail"], raw)
        repaired = None
        repair_reasons = []
        verified = raw_clean
        outcome = "accepted_first"
        if raw_reasons:
            repaired = model_generate(model, tokenizer, messages + [
                {"role": "assistant", "content": raw},
                {"role": "user", "content": REPAIR_PROMPT + "\nFailed checks: " + ", ".join(raw_reasons)},
            ])
            repaired_clean, repair_reasons = validate(row["head"], row["relation"], row["tail"], repaired)
            if repair_reasons:
                verified = row["template"]
                outcome = "manual_template_fallback"
            else:
                verified = repaired_clean
                outcome = "accepted_repair"
        rows.append({
            "class_id": row["class_id"], "triple_id": row["triple_id"],
            "head": row["head"], "kg_entity": row.get("kg_entity"),
            "relation": row["relation"], "tail": row["tail"],
            "manual_template": row["template"], "qwen_constrained": raw_clean,
            "first_check_failures": raw_reasons, "qwen_repair": repaired,
            "repair_check_failures": repair_reasons, "qwen_verified": verified,
            "verification_outcome": outcome,
        })
        if (i + 1) % 25 == 0:
            (prompt_dir / "generation_progress.json").write_text(
                json.dumps({"completed": False, "next_index": i + 1, "rows": rows}, ensure_ascii=False),
                encoding="utf-8")

    payload = {
        "completed": True, "dataset_dir": dataset_dir,
        "source_task": str(source), "model": "Qwen2.5-7B-Instruct",
        "model_path": str(MODEL_PATH), "decoding": {"do_sample": False, "max_new_tokens": 48},
        "system_prompt": SYSTEM_PROMPT, "rows": rows,
        "audit": dict(Counter(r["verification_outcome"] for r in rows)),
    }
    (prompt_dir / "qwen_generation_audit.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    del model, tokenizer
    gc.collect(); torch.cuda.empty_cache()
    return payload


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, str(path))
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


def metrics(ranks):
    values = np.asarray(ranks, dtype=np.float64)
    return {"Hit@1": float(100*np.mean(values <= 1)), "Hit@3": float(100*np.mean(values <= 3)),
            "Hit@5": float(100*np.mean(values <= 5)), "MRR": float(100*np.mean(1.0/values))}


def rank_of_true(scores, true_indices):
    order = torch.argsort(scores, descending=True).detach().cpu().tolist()
    return min(order.index(int(target)) + 1 for target in true_indices)


def normalized_lse(values, scale):
    return (torch.logsumexp(scale * values, dim=0) - math.log(values.numel())) / scale


def ours_fusion(base_score, evidence_scores, alpha, scale, top_p=5):
    if evidence_scores.numel() == 0: return base_score
    keep = torch.argsort(evidence_scores, descending=True, stable=True)[:top_p]
    pooled = normalized_lse(evidence_scores[keep], scale)
    return alpha * base_score + (1.0-alpha) * pooled


@torch.no_grad()
def evaluate_dataset(dataset_dir, generated):
    source = SOURCE_ROOT / dataset_dir
    out_dir = TASK_ROOT / dataset_dir
    results_dir = out_dir / "results"; cache_dir = out_dir / "cache"
    results_dir.mkdir(parents=True, exist_ok=True); cache_dir.mkdir(parents=True, exist_ok=True)
    source_script = load_module(source / "run_onehop_text_audit.py", "source_task06")
    base = source_script.load_runtime(); config = source_script.CONFIG; device = base.DEVICE
    clap = base.CLAP(version="2023", use_cuda=torch.cuda.is_available())
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        kge = torch.load(os.path.join(base.KGE_MODEL_DIR, "trained_model.pkl"), map_location=device)
    kge.eval(); _ = TriplesFactory.from_path(base.TRAIN_TRIPLES_PATH)
    dataset = base.load_dataset(); samples = list(base.iter_samples(dataset))
    source_cache = torch.load(source / "cache/onehop_text_cache.pt", map_location="cpu")
    labels = list(dataset["label_classes"])
    label_emb = F.normalize(base.get_safe_text_embeddings(clap, labels, device), dim=-1)

    rows_by_key = {(r["class_id"], r["triple_id"]): r for r in generated["rows"]}
    all_texts = []; class_index = []
    for class_id, cls in enumerate(source_cache["class_index"]):
        ids = {"manual": [], "qwen_constrained": [], "qwen_verified": []}
        for triple_id, _ in enumerate(cls["triples"]):
            row = rows_by_key[(class_id, triple_id)]
            for key, field in (("manual", "manual_template"), ("qwen_constrained", "qwen_constrained"),
                               ("qwen_verified", "qwen_verified")):
                ids[key].append(len(all_texts)); all_texts.append(row[field])
        class_index.append(ids)
    chunks=[]
    for start in range(0, len(all_texts), 128):
        chunks.append(F.normalize(base.get_safe_text_embeddings(clap, all_texts[start:start+128], device), dim=-1))
    evidence_emb = torch.cat(chunks) if chunks else torch.empty((0, label_emb.shape[1]), device=device)
    torch.save({"texts": all_texts, "class_index": class_index,
                "source_task06_signature": source_cache["signature"]}, cache_dir / "qwen_text_embeddings.pt")

    methods = ["CLAP", "Manual-Template", "Qwen-Constrained", "Qwen-Verified"]
    forms = [("manual", "Manual-Template"), ("qwen_constrained", "Qwen-Constrained"),
             ("qwen_verified", "Qwen-Verified")]
    ranks={m:[] for m in methods}; sample_rows=[]
    scale=float(config["logit_scale"])
    for sample_index, sample in enumerate(tqdm(samples, desc=f"Eval {dataset_dir}", mininterval=10)):
        if not os.path.exists(sample["audio_path"]) or not sample["true_indices"]: continue
        try:
            audio=F.normalize(base.to_tensor(clap.get_audio_embeddings([sample["audio_path"]])).to(device).float(), dim=-1)
        except Exception: continue
        base_scores=torch.matmul(audio,label_emb.T).squeeze(0)
        evidence_scores=torch.matmul(audio,evidence_emb.T).squeeze(0)
        top_indices=torch.argsort(base_scores,descending=True)[:5].tolist()
        alpha=float(np.clip(0.4+(0.8-0.4)*float(torch.max(base_scores)),0.4,0.8))
        vectors={m:base_scores.clone() for m in methods}
        for class_id in top_indices:
            for form,method in forms:
                ids=class_index[class_id][form]
                scores=evidence_scores[ids] if ids else torch.empty(0,device=device)
                vectors[method][class_id]=ours_fusion(base_scores[class_id],scores,alpha,scale,5)
        sr={m:rank_of_true(v,sample["true_indices"]) for m,v in vectors.items()}
        for m in methods: ranks[m].append(int(sr[m]))
        sample_rows.append({"sample_index":sample_index,"audio_path":sample["audio_path"],
                            "true_indices":[int(x) for x in sample["true_indices"]],"alpha":alpha,
                            "topk":top_indices,"ranks":sr})
        if len(sample_rows)%20==0:
            (results_dir/"progress.json").write_text(json.dumps({"completed":False,"samples":sample_rows},ensure_ascii=False),encoding="utf-8")
    table={m:metrics(ranks[m]) for m in methods}
    payload={"completed":True,"dataset":config["dataset"],
             "protocol":{"source_task":"06_onehop-text-verbalization-audit","only_changed_variable":"verbalization",
                         "top_k":5,"top_m":3,"fusion_top_p":5,"relations":config["relations"],"hop":1,
                         "mapping_sha256":source_script.sha256(source_script.MAPPING_FILE),"logit_scale":scale,
                         "alpha_min":0.4,"alpha_max":0.8},
             "generation_audit":generated["audit"],"metrics":table,"samples":sample_rows,
             "created_at":time.strftime("%Y-%m-%d %H:%M:%S")}
    (results_dir/"qwen_verified_results.json").write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8")
    lines=["method,Hit@1,Hit@3,Hit@5,MRR"]
    for m in methods:
        x=table[m]; lines.append(f"{m},{x['Hit@1']:.8f},{x['Hit@3']:.8f},{x['Hit@5']:.8f},{x['MRR']:.8f}")
    (results_dir/"qwen_verified_table.csv").write_text("\n".join(lines)+"\n",encoding="utf-8")
    (results_dir/"progress.json").write_text(json.dumps({"completed":True,"samples":sample_rows},ensure_ascii=False),encoding="utf-8")
    print(json.dumps(table,indent=2),flush=True)


def main():
    parser=argparse.ArgumentParser(); parser.add_argument("dataset_dir"); args=parser.parse_args()
    generated=generate_dataset(args.dataset_dir)
    evaluate_dataset(args.dataset_dir,generated)


if __name__ == "__main__": main()
