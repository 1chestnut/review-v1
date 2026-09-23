#!/usr/bin/env python3
"""P1-2: final online efficiency profile for CLAP, iKnow dagger, and SAKI."""
import os
os.environ['CUBLAS_WORKSPACE_CONFIG'] = ':4096:8'
os.environ['PYTHONHASHSEED'] = '42'
import argparse, csv, gc, hashlib, importlib.util, json, math, random, time
from collections import Counter, OrderedDict
from pathlib import Path
import numpy as np
import torch
import torch.nn.functional as F

ROOT = Path('/data/zkx/zkx/review1')
TASK = Path(os.environ.get('P1_2_TASK_ROOT', str(ROOT / '29.补充实验/P1_2_online_efficiency')))
AAKV = ROOT / '20A_topP5_aligned_selector_exploration/aakv_all.json'
METHODS = ('CLAP', 'iKnow_dagger', 'SAKI')
K, M, KAPPA, ALPHA, NR = 5, 3, 100.0, 0.3, 5
DS_DIR={'ESC-50':'01_ESC50','UrbanSound8K':'02_UrbanSound8K','FSD50K':'03_FSD50K','AudioSet':'05_AudioSet','TUT2017':'06_TUT2017'}

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
        elif method=='iKnow_dagger':
            z=base.clone()
            for ci in top:
                ev=(audio.reshape(1,-1)@frozen_emb[frozen_idx[ci]['direct']].T).reshape(-1);z[ci]=joint(base[ci],ev)
        else:z=final_one(base,audio.reshape(1,-1),top,relations,per_class,aakv_emb)
        outputs.append(z)
    return torch.stack(outputs)

def sync(): torch.cuda.synchronize()

def timed(fn):
    sync();torch.cuda.reset_peak_memory_stats();t0=time.perf_counter();value=fn();sync();elapsed=time.perf_counter()-t0
    return value,elapsed,torch.cuda.max_memory_allocated()

def batches(items,n):
    for i in range(0,len(items),n):yield items[i:i+n]

def final_samples(ds):
    if ds == 'TUT2017':
        path=ROOT/'28_TUT2017_full6300_rerun/main/test/06_TUT2017/samples.json'
        expected=6300
    else:
        path=ROOT/'25_final_experiment_alpha03_Nr5/test'/DS_DIR[ds]/'samples.json'
        expected={'ESC-50':2000,'UrbanSound8K':8732,'FSD50K':10231,'AudioSet':17233}[ds]
    rows=json.loads(path.read_text(encoding='utf-8'))
    if isinstance(rows,dict):
        rows=rows.get('samples',rows.get('records',rows))
    if len(rows)!=expected:raise RuntimeError(f'{ds}: final manifest count {len(rows)} != {expected}')
    ids=np.linspace(0,len(rows)-1,200,dtype=int).tolist()
    if len(set(ids))!=200:raise RuntimeError('duplicate profile sample indices')
    return path,[rows[i] for i in ids],ids,hashlib.sha256(path.read_bytes()).hexdigest()

def main(ds):
    seed_all();out=TASK/ds;out.mkdir(parents=True,exist_ok=True);src=ROOT/'12_shared-abcd-statistics'/DS_DIR[ds]
    rt=load_module(src/'frozen_inputs/runtime.py');dev=rt.DEVICE;clap=rt.CLAP(version='2023',use_cuda=True);clap.clap.eval()
    manifest,chosen,ids,manifest_sha=final_samples(ds);count=len(chosen)
    # Populate the operating-system file cache equally for all methods.
    # This is I/O preparation, not an additional model-inference warm-up.
    for sample in chosen:
        with open(sample['audio_path'],'rb') as audio_file:
            while audio_file.read(1024*1024):pass
    frozen=torch.load(src/'text_embeddings.pt',map_location='cpu');le=frozen['labels'].to(dev);fe_cpu=frozen['evidence'];fi=frozen['indices']
    cache=torch.load(ROOT/f'18a_relation_oracle_audit/{DS_DIR[ds]}/results/static_relation_cache.pt',map_location='cpu');relations=cache['relations']
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
    ae_cpu=torch.cat(chunks).cpu();del chunks
    gc.collect();torch.cuda.empty_cache()
    print(f'{ds}: offline evidence cache ready; {len(keys)} AAKV texts; {count} fixed samples',flush=True)
    label_bytes=le.numel()*le.element_size()
    index_bytes=len(json.dumps(fi,ensure_ascii=False,default=str).encode('utf-8'))
    relation_bytes=len(json.dumps(per,ensure_ascii=False,default=str).encode('utf-8'))
    cache_bytes={'CLAP':label_bytes,'iKnow_dagger':label_bytes+fe_cpu.numel()*fe_cpu.element_size()+index_bytes,
                 'SAKI':label_bytes+ae_cpu.numel()*ae_cpu.element_size()+relation_bytes}
    visible_gpu=os.environ.get('CUDA_VISIBLE_DEVICES','unspecified');gpu_name=torch.cuda.get_device_name(0);rows=[];reference_top1={}
    for bs in (1,32):
        for rep in range(5):
            order=METHODS[rep%3:]+METHODS[:rep%3]
            for method in order:
                fe=fe_cpu.to(dev) if method=='iKnow_dagger' else None
                ae=ae_cpu.to(dev) if method=='SAKI' else None
                warm=chosen[:20]
                for group in batches(warm,bs):
                    a=F.normalize(rt.to_tensor(clap.get_audio_embeddings([x['audio_path'] for x in group])).to(dev).float(),dim=-1)
                    run_method(method,a,le,fe,fi,relations,per,ae)
                sync()
                total_e2e=0.;total_stage=0.;peak=0;n=0;full_hash=hashlib.sha256();top1=[]
                for group in batches(chosen,bs):
                    paths=[x['audio_path'] for x in group]
                    # CLAP audio preprocessing can consume RNG state (e.g. crop/pad).
                    # Reset from the immutable batch identity before every live encoding,
                    # so rotated method order cannot change the audio representation.
                    batch_seed=int(hashlib.sha256(('42|'+ '|'.join(paths)).encode()).hexdigest()[:8],16)
                    seed_all(batch_seed)
                    audio,e2e_encode,mem1=timed(lambda:F.normalize(rt.to_tensor(clap.get_audio_embeddings(paths)).to(dev).float(),dim=-1))
                    scores,stage,mem2=timed(lambda:run_method(method,audio,le,fe,fi,relations,per,ae))
                    total_e2e += e2e_encode+stage;total_stage += stage;peak=max(peak,mem1,mem2);n+=len(group)
                    order=torch.argsort(scores,descending=True).cpu().numpy();full_hash.update(order.tobytes());top1.extend(order[:,0].tolist())
                key=(bs,method);digest=full_hash.hexdigest();top1_arr=np.asarray(top1,dtype=np.int64);top1_digest=hashlib.sha256(top1_arr.tobytes()).hexdigest()
                if key in reference_top1:
                    agreement=float(np.mean(reference_top1[key]==top1_arr))
                    if agreement < .995:raise RuntimeError(f'Top-1 repeat agreement below 99.5%: {key}={agreement:.6f}')
                else:reference_top1[key]=top1_arr.copy();agreement=1.0
                rows.append({'dataset':ds,'physical_gpu_id':visible_gpu,'gpu_name':gpu_name,'method':method,'batch_size':bs,'repeat':rep+1,'n_samples':n,
                    'end_to_end_ms_per_sample':1000*total_e2e/n,'knowledge_stage_ms_per_sample':1000*total_stage/n,
                    'throughput_samples_per_s':n/total_e2e,'peak_gpu_mib':peak/2**20,'offline_cache_mib':cache_bytes[method]/2**20,
                    'top1_agreement_vs_first_repeat':agreement,'top1_sha256':top1_digest,'full_ranking_sha256_audit':digest})
                print(f'{ds}: batch={bs} repeat={rep+1} method={method} latency={1000*total_e2e/n:.3f} ms/sample',flush=True)
                del fe,ae
                gc.collect();torch.cuda.empty_cache()
    with (out/'timing_repeats.csv').open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    summary=[]
    for bs in (1,32):
        for m in METHODS:
            rr=[x for x in rows if x['batch_size']==bs and x['method']==m];rec={'dataset':ds,'method':m,'batch_size':bs,'n_profiled':count,'repeats':5}
            for k in ('end_to_end_ms_per_sample','knowledge_stage_ms_per_sample','throughput_samples_per_s','peak_gpu_mib','offline_cache_mib'):
                a=np.asarray([x[k] for x in rr]);rec[k+'_mean']=float(a.mean());rec[k+'_std']=float(a.std(ddof=1))
            rec['minimum_top1_agreement_vs_first_repeat']=float(min(x['top1_agreement_vs_first_repeat'] for x in rr))
            summary.append(rec)
    with (out/'timing_summary.csv').open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=list(summary[0]));w.writeheader();w.writerows(summary)
    protocol={'task':'P1-2','dataset':ds,'physical_gpu_id':visible_gpu,'gpu_name':gpu_name,'comparison':list(METHODS),'sample_selection':'200 evenly spaced samples from final per-sample manifest; identical across methods',
      'final_manifest':str(manifest),'final_manifest_sha256':manifest_sha,'sample_manifest_positions':ids,
      'online_timing':{'end_to_end':'live audio decode/preprocess/CLAP audio encoding + method-specific scoring and ranking','knowledge_stage':'starts from current audio embedding; includes all method-specific matching, selection, fusion and ranking'},
      'offline_excluded':['KG entity mapping','RotatE Top-M tail retrieval','AAKV text generation','all text embedding computation'],
      'input_io_control':'All 200 selected audio files are read once before model timing to reduce method-order-dependent cold-file-cache effects; model warm-up remains 20 samples per method, batch size and repeat.',
      'offline_cache_size_definition':'float32 candidate label embeddings plus method-specific precomputed evidence embeddings and serialized evidence index mapping; excludes model weights, source KG, raw audio and generator',
      'fixed':{'model':'same CLAP checkpoint','device':'same physical GPU','K':K,'M':M,'kappa':KAPPA,'alpha':ALPHA,'Nr':NR,'hop':1,'TopP':'disabled','seed':42},
      'fairness':['all methods for a dataset use the same isolated physical GPU','different datasets may run concurrently on separate GPUs','GPU identity is recorded','same sample order','same immutable text caches','deterministic seed reset from each immutable audio-batch identity before live CLAP encoding','20-sample warm-up','CUDA synchronization around every timed segment','rotated method order','five repeats','Top-1 agreement across live re-encoding repeats must be at least 99.5%; complete ranking hashes are retained as an audit because near-tied low-ranked classes can exchange order'],
      'accuracy_source':'Task25 full-dataset metrics; timing subset is not used to re-estimate headline accuracy'}
    (out/'protocol.json').write_text(json.dumps(protocol,ensure_ascii=False,indent=2),encoding='utf-8')
    (out/'progress.json').write_text(json.dumps({'completed':True,'n_profiled':count},indent=2),encoding='utf-8')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('dataset');a=p.parse_args();main(a.dataset)
