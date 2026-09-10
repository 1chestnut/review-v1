import os
os.environ['CUBLAS_WORKSPACE_CONFIG'] = ':4096:8'
os.environ['PYTHONHASHSEED'] = '42'

import argparse, csv, hashlib, importlib.util, json, math, random
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from scipy.stats import binomtest
from tqdm import tqdm

ROOT = Path('/data/zkx/zkx/review1/16_second_hop_text_structure')
BASE = ROOT.parent
SOURCE12 = BASE / '12_shared-abcd-statistics'
SOURCE14 = BASE / '14_aakv_mp_potential'

K, M2, P, GAMMA = 5, 1, 5, 0.85
METHODS = ['D-1st', 'Flat-HalfEdge', 'FullPath-Chained', 'FullPath-TwoSentence', 'Endpoint']


def save(path, obj):
    path = Path(path); tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding='utf-8'); tmp.replace(path)


def digest(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod


def seed_all(x=42):
    random.seed(x); np.random.seed(x); torch.manual_seed(x); torch.cuda.manual_seed_all(x)


def pool(v): return (torch.logsumexp(100.0 * v, 0) - math.log(v.numel())) / 100.0


def fused(base, evidence, alpha):
    if not evidence.numel(): return base
    keep = torch.argsort(evidence, descending=True, stable=True)[:P]
    return alpha * base + (1.0 - alpha) * pool(evidence[keep])


def normalize_sentence(x):
    x = str(x).strip()
    return x if x.endswith(('.', '!', '?')) else x + '.'


def build_texts(ds, out):
    paths = json.loads((SOURCE14/ds/'paths_top5.json').read_text(encoding='utf-8'))
    second = json.loads((SOURCE14/ds/'aakv_generation.json').read_text(encoding='utf-8'))
    first = json.loads((SOURCE12/ds/'frozen_inputs/aakv.json').read_text(encoding='utf-8'))
    first_lookup = {}
    for row in first['rows']:
        key = (str(row.get('head','')), str(row.get('relation','')), str(row.get('tail','')))
        first_lookup[key] = normalize_sentence(row.get('qwen_verified') or row.get('manual_template') or '')
    second_lookup = {int(x['path_id']): x for x in second['rows']}
    rows=[]; audit={'exact_first_text':0,'fallback_first_text':0}
    for cls in paths['classes']:
        for p in cls:
            if int(p['kge_rank']) > M2: continue
            key=(str(p['origin']),str(p['r1']),str(p['middle']))
            first_text=first_lookup.get(key)
            if first_text: audit['exact_first_text'] += 1
            else:
                first_text=f"The sound of {p['origin']} has the relation {p['r1']} with {p['middle']}."
                audit['fallback_first_text'] += 1
            second_text=normalize_sentence(second_lookup[int(p['path_id'])]['aakv'])
            chained=(f"The sound of {p['origin']} is linked by the relation {p['r1']} to {p['middle']}, "
                     f"which is linked by the relation {p['r2']} to {p['tail']}.")
            rows.append({**p,
                'first_text':first_text,
                'second_text':second_text,
                'FullPath-Chained':chained,
                'FullPath-TwoSentence':first_text+' '+second_text,
                'Endpoint':f"The sound of {p['origin']} is associated with {p['tail']}."})
    obj={'dataset':ds,'M2':M2,'rows':rows,'audit':audit,
         'note':'Flat-HalfEdge is loaded exactly from Task14; the other variants use identical paths.'}
    save(out/'texts.json',obj); return obj


@torch.inference_mode()
def embed_variants(runtime, clap, text_obj, out, dim):
    cache=out/'text_embeddings.pt'; sig=digest(out/'texts.json')
    if cache.exists():
        obj=torch.load(cache,map_location='cuda')
        if obj['signature']==sig:
            obj['embeddings']=obj['embeddings'].to('cuda'); return obj
    texts=[]; index={m:{} for m in METHODS[2:]}; seen={}
    for row in text_obj['rows']:
        for m in METHODS[2:]:
            t=row[m]
            if t not in seen: seen[t]=len(texts); texts.append(t)
            index[m][int(row['path_id'])]=seen[t]
    chunks=[]
    for i in tqdm(range(0,len(texts),128),desc='CLAP path text',mininterval=10):
        chunks.append(F.normalize(runtime.get_safe_text_embeddings(clap,texts[i:i+128],'cuda'),dim=-1))
    emb=torch.cat(chunks) if chunks else torch.empty((0,dim),device='cuda')
    obj={'signature':sig,'texts':texts,'index':index,'embeddings':emb.cpu()};torch.save(obj,cache)
    obj['embeddings']=emb;return obj


def metrics_from_ranks(r):
    return {'Hit@1':float(100*np.mean(r<=1)),'Hit@3':float(100*np.mean(r<=3)),
            'Hit@5':float(100*np.mean(r<=5)),'MRR':float(100*np.mean(1/r))}


def statistics(ranks, out):
    rng=np.random.default_rng(42); rows=[]
    base=ranks[:,0]
    for j,m in enumerate(METHODS[1:],1):
        dh=100*((ranks[:,j]<=1).astype(float)-(base<=1).astype(float));dr=100*(1/ranks[:,j]-1/base)
        boot=np.empty((10000,2))
        for k in range(10000):
            ix=rng.integers(0,len(base),len(base));boot[k]=[dh[ix].mean(),dr[ix].mean()]
        gain=int(np.sum((ranks[:,j]==1)&(base!=1)));loss=int(np.sum((ranks[:,j]!=1)&(base==1)))
        rows.append({'comparison':m+' - D-1st','delta_Hit@1_pp':float(dh.mean()),
          'Hit@1_CI95':np.quantile(boot[:,0],[.025,.975]).tolist(),'delta_MRR_pp':float(dr.mean()),
          'MRR_CI95':np.quantile(boot[:,1],[.025,.975]).tolist(),'wrong_to_right':gain,
          'right_to_wrong':loss,'mcnemar_p':float(binomtest(gain,gain+loss,.5).pvalue) if gain+loss else 1.0,
          'rank_improved':int(np.sum(ranks[:,j]<base)),'rank_worsened':int(np.sum(ranks[:,j]>base))})
    save(out/'paired_statistics.json',{'bootstrap':10000,'seed':42,'rows':rows});return rows


@torch.inference_mode()
def run(ds):
    seed_all();torch.use_deterministic_algorithms(True);torch.backends.cudnn.benchmark=False
    torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
    out=ROOT/ds;out.mkdir(parents=True,exist_ok=True)
    runtime_path=SOURCE12/ds/'frozen_inputs/runtime.py';runtime=load_module(runtime_path,'runtime_'+ds)
    text_obj=build_texts(ds,out)
    first=torch.load(SOURCE12/ds/'text_embeddings.pt',map_location='cuda')
    label_emb=first['labels'].to('cuda');first_emb=first['evidence'].to('cuda');first_index=first['indices']
    old=np.load(SOURCE14/ds/'predictions.npz',allow_pickle=True);old_methods=[str(x) for x in old['methods']]
    old_scores=old['scores']; d_ix=old_methods.index('1st-P5'); flat_ix=old_methods.index('AAKV-M1-P5')
    clap=runtime.CLAP(version='2023',use_cuda=True);clap.clap.eval()
    emb_obj=embed_variants(runtime,clap,text_obj,out,label_emb.shape[1]);emb=emb_obj['embeddings']
    by_class=[[] for _ in range(label_emb.shape[0])]
    for row in text_obj['rows']:by_class[int(row['class_id'])].append(row)
    samples=list(runtime.iter_samples(runtime.load_dataset()));ranks=[];scores=[];records=[]
    assert len(samples)==old_scores.shape[0]
    for si,s in enumerate(tqdm(samples,desc=ds,mininterval=10)):
        audio=torch.load(SOURCE12/ds/'audio_cache'/f'{si:06d}.pt',map_location='cuda')
        b=(audio@label_emb.T).squeeze(0);e1=(audio@first_emb.T).squeeze(0);ep=(audio@emb.T).squeeze(0)
        vec={'D-1st':torch.as_tensor(old_scores[si,d_ix],device='cuda'),
             'Flat-HalfEdge':torch.as_tensor(old_scores[si,flat_ix],device='cuda')}
        for m in METHODS[2:]: vec[m]=b.clone()
        top=torch.argsort(b,descending=True)[:K].tolist();alpha=float(np.clip(.4+.4*float(b.max()),.4,.8))
        for ci in top:
            ids1=first_index[ci]['aakv'];s1=e1[ids1] if ids1 else torch.empty(0,device='cuda')
            rows=by_class[ci]
            for m in METHODS[2:]:
                ids=[emb_obj['index'][m][int(x['path_id'])] for x in rows]
                h2=ep[ids] if ids else torch.empty(0,device='cuda')
                vec[m][ci]=fused(b[ci],torch.cat([s1,GAMMA*h2]),alpha)
        arr=torch.stack([vec[m] for m in METHODS]);order=torch.argsort(arr,dim=1,descending=True).cpu().numpy()
        sr=[min(int(np.where(o==y)[0][0])+1 for y in s['true_indices']) for o in order]
        ranks.append(sr);scores.append(arr.cpu().numpy());records.append({'sample_index':si,'audio_path':s['audio_path'],
          'true_indices':[int(x) for x in s['true_indices']],'ranks':dict(zip(METHODS,sr))})
        if (si+1)%100==0:save(out/'progress.json',{'done':si+1,'total':len(samples)})
    ranks=np.asarray(ranks);metrics={m:metrics_from_ranks(ranks[:,j]) for j,m in enumerate(METHODS)}
    save(out/'metrics.json',metrics);save(out/'samples.json',records)
    with (out/'metrics.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.writer(f);w.writerow(['method','Hit@1','Hit@3','Hit@5','MRR'])
        for m in METHODS:w.writerow([m]+[metrics[m][q] for q in ['Hit@1','Hit@3','Hit@5','MRR']])
    stats=statistics(ranks,out)
    np.savez_compressed(out/'predictions.npz',scores=np.asarray(scores),ranks=ranks,methods=np.asarray(METHODS))
    save(out/'protocol.json',{'purpose':'Isolate second-hop textual organization','frozen':{'source':'Task14',
      'K':K,'M1':3,'M2':M2,'P_total':P,'gamma':GAMMA,'gate':False,'aggregation':'Task14 unchanged'},
      'varied_only':'second-hop textual organization','methods':METHODS,
      'important':'Flat-HalfEdge is Task14 AAKV-M1-P5 exactly; no duplicate flat method was invented.',
      'runtime_sha256':digest(runtime_path)})
    save(out/'progress.json',{'completed':True,'done':len(samples),'total':len(samples)})
    print(json.dumps({'dataset':ds,'metrics':metrics,'statistics':stats,'text_audit':text_obj['audit']},indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('dataset');a=p.parse_args();run(a.dataset)
