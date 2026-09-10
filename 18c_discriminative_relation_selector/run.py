#!/usr/bin/env python3
"""Task18C: label-free discriminative one-hop relation selectors."""
import os
os.environ["CUBLAS_WORKSPACE_CONFIG"] = ":4096:8"
os.environ["PYTHONHASHSEED"] = "42"
import argparse, hashlib, importlib.util, json, random, time
from collections import Counter, OrderedDict
from pathlib import Path
import numpy as np
import torch
import torch.nn.functional as F
from tqdm import tqdm

METHODS=["CLAP","Frozen-iKnow","Abs-Top3","Margin-Top1","Margin-Top3",
         "Entropy-Top1","Entropy-Top3","Consensus-Margin-Top1",
         "Consensus-Margin-Top3","Relation-Oracle-analysis-only"]

def mod(p):
 s=importlib.util.spec_from_file_location("rt18c",str(p));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def seed_audio(p):
 z=int(hashlib.sha256(("42|"+p).encode()).hexdigest()[:8],16);random.seed(z);np.random.seed(z%(2**32-1));torch.manual_seed(z)
 if torch.cuda.is_available():torch.cuda.manual_seed_all(z)
 return z
def nlse(b,e,k):
 z=torch.cat([b.reshape(1)*k,e*k]);return (torch.logsumexp(z,0)-np.log(z.numel()))/k
def enlse(e,k):return (torch.logsumexp(e*k,0)-np.log(e.numel()))/k
def rank(s,t):
 o=torch.argsort(s,descending=True).detach().cpu().numpy();return min(int(np.where(o==i)[0][0])+1 for i in t)
def metric(r):
 x=np.asarray(r,float);return {"Hit@1":float(np.mean(x<=1)*100),"Hit@3":float(np.mean(x<=3)*100),"Hit@5":float(np.mean(x<=5)*100),"MRR":float(np.mean(1/x)*100)}
def save(p,x):
 p=Path(p);q=p.with_suffix(p.suffix+".tmp");q.write_text(json.dumps(x,ensure_ascii=False));os.replace(q,p)
def apply(base,pc,rels,k):
 out=base.clone()
 for ci,rd in pc.items():
  merged=OrderedDict()
  for r in rels:
   for tail,score in rd.get(r,[]):merged.setdefault(tail,score)
  if merged:out[ci]=nlse(base[ci],torch.stack(list(merged.values())),k)
 return out

def main():
 a=argparse.ArgumentParser();a.add_argument("--dataset-dir",required=True);a.add_argument("--task18a-result",required=True);a.add_argument("--task18a-cache",required=True);a.add_argument("--output-dir",required=True);x=a.parse_args()
 d=Path(x.dataset_dir);out=Path(x.output_dir);out.mkdir(parents=True,exist_ok=True);cfg=json.loads((d/"config.json").read_text());base=mod(d/"iknow_runtime.py")
 a18=json.loads(Path(x.task18a_result).read_text());oracle={int(v["sample_index"]):int(v["oracle_rank"]) for v in a18["rows"]};cache=torch.load(x.task18a_cache,map_location="cpu")
 rels=cache["relations"];tails=cache["tails"];pidx={p:i for i,p in enumerate(cache["prompts"])};frozen=[r for r in cfg["relations"] if r in rels]
 seed_audio("task18c-initialization");torch.use_deterministic_algorithms(True);torch.backends.cudnn.benchmark=False;torch.backends.cudnn.deterministic=True;torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
 dev=base.DEVICE;clap=base.CLAP(version="2023",use_cuda=torch.cuda.is_available());data=base.load_dataset();labels=list(data["label_classes"]);samples=list(base.iter_samples(data));le=F.normalize(base.get_safe_text_embeddings(clap,labels,dev),dim=-1);pe=cache["prompt_embeddings"].to(dev);K=int(cfg["top_k"]);scale=float(cfg["logit_scale"])
 pp=out/"progress.json";st=json.loads(pp.read_text()) if pp.exists() else {"next":0,"rows":[]};rows=st["rows"]
 counts={m:Counter() for m in METHODS if "Top" in m and m not in ["CLAP"]}
 for old in rows:
  for m,rs in old.get("selected_relations",{}).items():counts[m].update(rs)
 for si in tqdm(range(int(st["next"]),len(samples)),total=len(samples),initial=int(st["next"]),desc=cfg["dataset"],mininterval=10):
  s=samples[si]
  if not os.path.exists(s["audio_path"]) or not s["true_indices"]:raise RuntimeError(f"invalid sample {si}")
  sd=seed_audio(s["audio_path"]);audio=F.normalize(base.to_tensor(clap.get_audio_embeddings([s["audio_path"]])).to(dev).float(),dim=-1);bs=(audio@le.T).squeeze(0);top=torch.argsort(bs,descending=True)[:K].tolist();pc={};absu={r:[] for r in rels}
  for ci in top:
   pc[ci]={}
   for r in rels:
    it=tails[r].get(ci,[])
    if not it:absu[r].append(-1.0);continue
    ids=[pidx[p] for _,p in it];ev=(audio@pe[ids].T).reshape(-1);pc[ci][r]=[(tail,score) for (tail,_),score in zip(it,ev)];absu[r].append(float(enlse(ev,scale)))
  single={r:apply(bs,pc,[r],scale) for r in rels};margin={};entropy={};pred={}
  for r,z in single.items():
   vals=torch.topk(z,k=min(2,z.numel())).values;margin[r]=float((vals[0]-vals[1]).item()) if vals.numel()>1 else 0.0
   prob=torch.softmax(z*scale,dim=0);entropy[r]=float((-(prob*torch.log(prob.clamp_min(1e-12))).sum()).item());pred[r]=int(torch.argmax(z).item())
  abs_order=sorted(rels,key=lambda r:(-float(np.mean(absu[r])),r));mar_order=sorted(rels,key=lambda r:(-margin[r],r));ent_order=sorted(rels,key=lambda r:(entropy[r],r))
  votes=Counter(pred.values());maxvote=max(votes.values());cands=sorted(c for c,n in votes.items() if n==maxvote);cons_class=max(cands,key=lambda c:(sum(margin[r] for r in rels if pred[r]==c),-c));support=sorted([r for r in rels if pred[r]==cons_class],key=lambda r:(-margin[r],r));cons_order=support+[r for r in mar_order if r not in support]
  sel={"Abs-Top3":abs_order[:3],"Margin-Top1":mar_order[:1],"Margin-Top3":mar_order[:3],"Entropy-Top1":ent_order[:1],"Entropy-Top3":ent_order[:3],"Consensus-Margin-Top1":cons_order[:1],"Consensus-Margin-Top3":cons_order[:3]}
  for m,rs in sel.items():counts[m].update(rs)
  scores={"CLAP":bs,"Frozen-iKnow":apply(bs,pc,frozen,scale)}
  for m,rs in sel.items():scores[m]=apply(bs,pc,rs,scale)
  ranks={m:rank(z,s["true_indices"]) for m,z in scores.items()};ranks["Relation-Oracle-analysis-only"]=oracle[si]
  rows.append({"sample_index":si,"audio_path":s["audio_path"],"true_indices":[int(i) for i in s["true_indices"]],"audio_seed":sd,"selected_relations":sel,"consensus_class_index":cons_class,"consensus_votes":maxvote,"ranks":ranks})
  if (si+1)%20==0:save(pp,{"next":si+1,"rows":rows})
 met={m:metric([v["ranks"][m] for v in rows]) for m in METHODS};res={"completed":True,"dataset":cfg["dataset"],"n":len(rows),"protocol":{"hop":1,"base":"Task05b","seed":"Task12 SHA256 path rule","top_k":K,"top_m":cfg["top_m"],"text":"class_name, tail","labels_used_by_selector":False,"softmax_scale":scale,"only_changed_variable":"relation selection score"},"metrics":met,"selection_counts":{m:dict(c) for m,c in counts.items()},"rows":rows,"created_at":time.strftime("%F %T")};save(out/"discriminative_selector_results.json",res)
 lines=["method,Hit@1,Hit@3,Hit@5,MRR"]+[f"{m},{met[m]['Hit@1']:.8f},{met[m]['Hit@3']:.8f},{met[m]['Hit@5']:.8f},{met[m]['MRR']:.8f}" for m in METHODS];(out/"discriminative_selector_table.csv").write_text("\n".join(lines)+"\n");save(pp,{"next":len(samples),"rows":rows});print(json.dumps(met,indent=2))
if __name__=="__main__":main()
