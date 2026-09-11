#!/usr/bin/env python3
"""Task25(a): fair cached efficiency profile for CLAP, Frozen-iKnow, Final-TFS."""
import os
os.environ['CUBLAS_WORKSPACE_CONFIG'] = ':4096:8'
os.environ['PYTHONHASHSEED'] = '42'
import argparse, csv, hashlib, importlib.util, json, math, random, time
from collections import Counter, OrderedDict
from pathlib import Path
import numpy as np
import torch
import torch.nn.functional as F

ROOT = Path('/data/zkx/zkx/review1')
TASK = ROOT / '25a_fair_cached_efficiency'
AAKV = ROOT / '20A_topP5_aligned_selector_exploration/aakv_all.json'
METHODS = ('CLAP', 'Frozen-iKnow', 'Final-TFS')
K, M, KAPPA, ALPHA, NR = 5, 3, 100.0, 0.3, 5

def seed_all(v=42):
    random.seed(v); np.random.seed(v); torch.manual_seed(v); torch.cuda.manual_seed_all(v)

def load_module(path):
    spec=importlib.util.spec_from_file_location('rt25a',str(path));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def nlse(v): return (torch.logsumexp(KAPPA*v,0)-math.log(v.numel()))/KAPPA
def joint(b,e): return b if not e.numel() else nlse(torch.cat((b.reshape(1),e.reshape(-1))))
def hier(b,e): return b if not e.numel() else ALPHA*b+(1-ALPHA)*nlse(e.reshape(-1))

def relation_order(spaces, relations):
    pred={};margin={}
    for r in relations:
        vals=torch.topk(spaces[r],k=min(2,spaces[r].numel())).values
        pred[r]=int(torch.argmax(spaces[r]));margin[r]=float(vals[0]-vals[1]) if vals.numel()>1 else 0.
    votes=Counter(pred.values());mv=max(votes.values());cand=sorted(c for c,n in votes.items() if n==mv)
    cc=max(cand,key=lambda c:(sum(margin[r] for r in relations if pred[r]==c),-c))
    mo=sorted(relations,key=lambda r:(-margin[r],r));support=sorted((r for r in relations if pred[r]==cc),key=lambda r:(-margin[r],r))
    return support+[r for r in mo if r not in support]

def final_one(base,audio,top,relations,per,ae):
    spaces={}
    for r in relations:
        z=base.clone()
        for ci in top:
            ids=[idx for tail,idx in per[ci][r]];ev=audio.new_empty(0) if not ids else (audio@ae[ids].T).reshape(-1)
            z[ci]=hier(base[ci],ev)
        spaces[r]=z
    chosen=relation_order(spaces,relations)[:NR];z=base.clone()
    for ci in top:
        merged=OrderedDict()
        for r in chosen:
            for tail,idx in per[ci][r]:merged.setdefault(tail,idx)
        ids=list(merged.values());ev=audio.new_empty(0) if not ids else (audio@ae[ids].T).reshape(-1)
        z[ci]=hier(base[ci],ev)
    return z

def run_method(method,audios,label_emb,frozen_emb,frozen_idx,relations,per_class,aakv_emb):
    outputs=[]
    for audio in audios:
        base=(audio.reshape(1,-1)@label_emb.T).squeeze(0);top=torch.argsort(base,descending=True)[:K].tolist()
        if method=='CLAP': z=base
        elif method=='Frozen-iKnow':
            z=base.clone()
            for ci in top:
                ev=(audio.reshape(1,-1)@frozen_emb[frozen_idx[ci]['direct']].T).reshape(-1);z[ci]=joint(base[ci],ev)
        else:z=final_one(base,audio.reshape(1,-1),top,relations,per_class,aakv_emb)
        outputs.append(z)
    return torch.stack(outputs)

def sync(): torch.cuda.synchronize()

def timed(fn):
    sync();torch.cuda.reset_peak_memory_stats();before=torch.cuda.memory_allocated();t0=time.perf_counter();value=fn();sync();elapsed=time.perf_counter()-t0
    return value,elapsed,max(0,torch.cuda.max_memory_allocated()-before)

def batches(items,n):
    for i in range(0,len(items),n):yield items[i:i+n]

def main(ds):
    seed_all();out=TASK/ds;out.mkdir(parents=True,exist_ok=True);src=ROOT/'12_shared-abcd-statistics'/ds
    rt=load_module(src/'frozen_inputs/runtime.py');dev=rt.DEVICE;clap=rt.CLAP(version='2023',use_cuda=True);clap.clap.eval()
    samples=list(rt.iter_samples(rt.load_dataset()));count=min(200,len(samples));ids=np.linspace(0,len(samples)-1,count,dtype=int).tolist();chosen=[samples[i] for i in ids]
    frozen=torch.load(src/'text_embeddings.pt',map_location='cpu');le=frozen['labels'].to(dev);fe=frozen['evidence'].to(dev);fi=frozen['indices']
    cache=torch.load(ROOT/f'18a_relation_oracle_audit/{ds}/results/static_relation_cache.pt',map_location='cpu');relations=cache['relations']
    texts=json.loads(AAKV.read_text(encoding='utf-8'))['texts'];keys=[];seen=set();per={}
    for r in relations:
        for ci,items in cache['tails'][r].items():
            per.setdefault(int(ci),{}).setdefault(r,[])
            for tail,prompt in items:
                key='\t'.join((prompt.split(', ',1)[0],r,tail))
                if key not in seen:seen.add(key);keys.append(key)
                per[int(ci)][r].append((tail,key))
    for ci in range(le.shape[0]):
        per.setdefault(ci,{})
        for r in relations:per[ci].setdefault(r,[])
    key_id={k:i for i,k in enumerate(keys)}
    per={ci:{r:[(tail,key_id[key]) for tail,key in vals] for r,vals in rv.items()} for ci,rv in per.items()}
    chunks=[]
    for i in range(0,len(keys),128):chunks.append(F.normalize(rt.get_safe_text_embeddings(clap,[texts[k] for k in keys[i:i+128]],dev),dim=-1))
    ae=torch.cat(chunks)
    static_bytes=sum(x.numel()*x.element_size() for x in (le,fe,ae))
    # Warm-up includes live audio encoding and every online branch.
    warm=chosen[:min(20,len(chosen))]
    for group in batches(warm,4):
        a=F.normalize(rt.to_tensor(clap.get_audio_embeddings([x['audio_path'] for x in group])).to(dev).float(),dim=-1)
        for m in METHODS:run_method(m,a,le,fe,fi,relations,per,ae)
    visible_gpu=os.environ.get('CUDA_VISIBLE_DEVICES','unspecified');gpu_name=torch.cuda.get_device_name(0);rows=[];reference={}
    for bs in (1,32):
        for rep in range(5):
            order=METHODS[rep%3:]+METHODS[:rep%3]
            for method in order:
                total_e2e=0.;total_stage=0.;peak=0;n=0;hash_acc=hashlib.sha256()
                for group in batches(chosen,bs):
                    paths=[x['audio_path'] for x in group]
                    audio,e2e_encode,mem1=timed(lambda:F.normalize(rt.to_tensor(clap.get_audio_embeddings(paths)).to(dev).float(),dim=-1))
                    scores,stage,mem2=timed(lambda:run_method(method,audio,le,fe,fi,relations,per,ae))
                    total_e2e += e2e_encode+stage;total_stage += stage;peak=max(peak,mem1,mem2);n+=len(group)
                    hash_acc.update(torch.argsort(scores,descending=True).cpu().numpy().tobytes())
                key=(bs,method);digest=hash_acc.hexdigest()
                if key in reference and reference[key]!=digest:raise RuntimeError(f'non-deterministic ranking: {key}')
                reference[key]=digest
                rows.append({'dataset':ds,'physical_gpu_id':visible_gpu,'gpu_name':gpu_name,'method':method,'batch_size':bs,'repeat':rep+1,'n_samples':n,
                    'end_to_end_ms_per_sample':1000*total_e2e/n,'knowledge_stage_ms_per_sample':1000*total_stage/n,
                    'throughput_samples_per_s':n/total_e2e,'incremental_peak_gpu_mib':peak/2**20,'static_cache_mib':static_bytes/2**20,
                    'ranking_sha256':digest})
    with (out/'timing_repeats.csv').open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    summary=[]
    for bs in (1,32):
        for m in METHODS:
            rr=[x for x in rows if x['batch_size']==bs and x['method']==m];rec={'dataset':ds,'method':m,'batch_size':bs,'n_profiled':count,'repeats':5}
            for k in ('end_to_end_ms_per_sample','knowledge_stage_ms_per_sample','throughput_samples_per_s','incremental_peak_gpu_mib','static_cache_mib'):
                a=np.asarray([x[k] for x in rr]);rec[k+'_mean']=float(a.mean());rec[k+'_std']=float(a.std(ddof=1))
            summary.append(rec)
    with (out/'timing_summary.csv').open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=list(summary[0]));w.writeheader();w.writerows(summary)
    protocol={'task':'25(a)','dataset':ds,'physical_gpu_id':visible_gpu,'gpu_name':gpu_name,'comparison':list(METHODS),'sample_selection':'200 evenly spaced samples; identical across methods',
      'online_timing':{'end_to_end':'live audio decode/preprocess/CLAP audio encoding + method-specific scoring and ranking','knowledge_stage':'starts from current audio embedding; includes all method-specific matching, selection, fusion and ranking'},
      'offline_excluded':['KG entity mapping','RotatE Top-M tail retrieval','AAKV text generation','all text embedding computation'],
      'fixed':{'model':'same CLAP checkpoint','device':'same physical GPU','K':K,'M':M,'kappa':KAPPA,'alpha':ALPHA,'Nr':NR,'hop':1,'TopP':'disabled','seed':42},
      'fairness':['all methods for a dataset use the same isolated physical GPU','different datasets may run concurrently on separate GPUs','GPU identity is recorded','same sample order','same immutable text caches','20-sample warm-up','CUDA synchronization around every timed segment','rotated method order','five repeats','ranking hash equality across repeats'],
      'accuracy_source':'Task25 full-dataset metrics; timing subset is not used to re-estimate headline accuracy'}
    (out/'protocol.json').write_text(json.dumps(protocol,ensure_ascii=False,indent=2),encoding='utf-8')
    (out/'progress.json').write_text(json.dumps({'completed':True,'n_profiled':count},indent=2),encoding='utf-8')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('dataset');a=p.parse_args();main(a.dataset)
