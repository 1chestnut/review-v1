import os
os.environ['CUBLAS_WORKSPACE_CONFIG'] = ':4096:8'
os.environ['PYTHONHASHSEED'] = '42'

import argparse, csv, gc, hashlib, importlib.util, json, math, random, time
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from pykeen.triples import TriplesFactory
from scipy.stats import binomtest
from tqdm import tqdm
from transformers import AutoModelForCausalLM, AutoTokenizer

ROOT = Path('/data/zkx/zkx/review1/14_aakv_mp_potential')
BASE = ROOT.parent
SOURCE12 = BASE / '12_shared-abcd-statistics'
SOURCE13 = BASE / '13_controlled_second_hop'
TASK10_CODE = BASE / '10_hard-prefix-pilot/code/run_qwen_verified.py'
MODEL_PATH = Path('/data/zkx/zkx/iknow-audio/data/model/千问')

K = 5
M1 = 3
M_VALUES = [1, 3, 5]
P_VALUES = [3, 5, 10]
GAMMA = 0.85
BASELINES = [f'1st-P{p}' for p in P_VALUES]
GRID = [f'AAKV-M{m}-P{p}' for p in P_VALUES for m in M_VALUES]
METHODS = BASELINES + ['Fallback-M1-P5'] + GRID


def save(path, obj):
    path = Path(path); tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding='utf-8')
    tmp.replace(path)


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod


def seed_all(x):
    random.seed(x); np.random.seed(x); torch.manual_seed(x); torch.cuda.manual_seed_all(x)


def digest(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def pool(v): return (torch.logsumexp(100.0 * v, 0) - math.log(v.numel())) / 100.0


def fused(base, evidence, alpha, p):
    if not evidence.numel(): return base, torch.empty(0, dtype=torch.long, device=evidence.device)
    keep = torch.argsort(evidence, descending=True, stable=True)[:p]
    return alpha * base + (1.0 - alpha) * pool(evidence[keep]), keep


def build_paths(ds, runtime, cfg, triples, out):
    path = out / 'paths_top5.json'
    signature = {'dataset': ds, 'relations': cfg['relations'], 'M2_max': 5,
                 'origin_mapping_logic': 'class.mapped_entity_then_first_triple_head_v2',
                 'triples_sha256': digest(out/'frozen_inputs/triples.json')}
    if path.exists():
        obj = json.loads(path.read_text(encoding='utf-8'))
        if obj.get('signature') == signature: return obj
    model = torch.load(Path(runtime.KGE_MODEL_DIR)/'trained_model.pkl', map_location=runtime.DEVICE)
    model.eval(); factory = TriplesFactory.from_path(runtime.TRAIN_TRIPLES_PATH)
    runtime.TOP_M = 5; get_tails = runtime.build_tail_predictor(model, factory)
    relations = [r for r in cfg['relations'] if r in factory.relation_to_id]
    audit = Counter(); classes=[]; path_id=0
    for ci, cls in enumerate(tqdm(triples['classes'], desc=f'{ds} paths', mininterval=5)):
        origin = str(cls.get('mapped_entity') or
                     (cls['triples'][0]['head'] if cls.get('triples') else ''))
        origin_id = factory.entity_to_id.get(origin); seen=set(); rows=[]
        for first in cls['triples']:
            middle = str(first['tail']); middle_id = factory.entity_to_id.get(middle)
            audit['first_hop_entities'] += 1
            if middle_id is None:
                audit['middle_not_in_entity_vocab'] += 1; continue
            audit['middle_valid_as_second_head'] += 1
            for r2 in relations:
                audit['queries'] += 1; tails=get_tails(middle, r2)
                if not tails: audit['empty_queries'] += 1
                for rank, tail0 in enumerate(tails[:5], 1):
                    tail=str(tail0); tail_id=factory.entity_to_id.get(tail)
                    if tail_id is None: audit['tail_not_in_vocab'] += 1; continue
                    if tail_id == middle_id: audit['self_loop_removed'] += 1; continue
                    if origin_id is not None and tail_id == origin_id:
                        audit['return_origin_removed'] += 1; continue
                    key=(middle_id, factory.relation_to_id[r2], tail_id)
                    if key in seen: audit['duplicate_path_removed'] += 1; continue
                    seen.add(key)
                    rows.append({'path_id':path_id,'class_id':ci,'origin':origin,
                      'origin_id':origin_id,'r1':first['relation'],'middle':middle,
                      'middle_id':middle_id,'r2':r2,'r2_id':factory.relation_to_id[r2],
                      'tail':tail,'tail_id':tail_id,'kge_rank':rank,
                      'fallback':f'The sound of {middle} has the relation {r2} with {tail}.'})
                    path_id += 1; audit['retained'] += 1
        if not rows: audit['classes_without_paths'] += 1
        classes.append(rows)
    audit.update(classes=len(classes), valid_relations=len(relations),
                 invalid_relations=len(cfg['relations'])-len(relations))
    obj={'signature':signature,'audit':dict(audit),'valid_relations':relations,'classes':classes}
    save(path,obj); del model; torch.cuda.empty_cache(); return obj


def generate_aakv(ds, paths, out):
    final_path=out/'aakv_generation.json'; jsonl=out/'aakv_rows.jsonl'
    flat=[x for cls in paths['classes'] for x in cls]
    existing=[]
    if jsonl.exists():
        with jsonl.open(encoding='utf-8') as f:
            for line in f:
                if line.strip(): existing.append(json.loads(line))
    if final_path.exists():
        obj=json.loads(final_path.read_text(encoding='utf-8'))
        if obj.get('completed') and len(obj['rows'])==len(flat): return obj
    assert all(existing[i]['path_id']==flat[i]['path_id'] for i in range(len(existing)))
    verbalizer=load_module(TASK10_CODE,'task10_verbalizer')
    tokenizer=AutoTokenizer.from_pretrained(MODEL_PATH,local_files_only=True)
    model=AutoModelForCausalLM.from_pretrained(MODEL_PATH,torch_dtype=torch.bfloat16,
                                               device_map='cuda:0',local_files_only=True)
    model.eval(); rows=list(existing)
    def generate(messages):
        # The local tokenizer snapshot does not persist chat_template.  Use the
        # canonical Qwen2.5 ChatML serialization explicitly and deterministically.
        prompt=''.join(f"<|im_start|>{m['role']}\n{m['content']}<|im_end|>\n" for m in messages)
        prompt += '<|im_start|>assistant\n'
        inputs=tokenizer([prompt],return_tensors='pt').to(model.device)
        with torch.inference_mode():
            ids=model.generate(**inputs,max_new_tokens=48,do_sample=False,
                               pad_token_id=tokenizer.eos_token_id)
        return tokenizer.decode(ids[0,inputs.input_ids.shape[1]:],skip_special_tokens=True).strip()
    with jsonl.open('a',encoding='utf-8') as f:
        for row in tqdm(flat[len(rows):],desc=f'{ds} AAKV',mininterval=10,initial=len(rows),total=len(flat)):
            head,relation,tail=row['middle'],row['r2'],row['tail']
            user=f'[head] {head}\n[relation] {relation}\n[tail] {tail}'
            system=verbalizer.SYSTEM_PROMPT.replace('{head}',head)
            repair_prompt=verbalizer.REPAIR_PROMPT.replace('{head}',head)
            messages=[{'role':'system','content':system},{'role':'user','content':user}]
            raw=generate(messages)
            clean,reasons=verbalizer.validate(head,relation,tail,raw)
            repair=None; repair_reasons=[]; verified=clean; outcome='accepted_first'
            if reasons:
                repair=generate(messages+[
                    {'role':'assistant','content':raw},
                    {'role':'user','content':repair_prompt+'\nFailed checks: '+', '.join(reasons)}])
                repaired,repair_reasons=verbalizer.validate(head,relation,tail,repair)
                if repair_reasons:
                    verified=row['fallback']; outcome='universal_fallback'
                else: verified=repaired; outcome='accepted_repair'
            rec={**row,'raw':clean,'first_failures':reasons,'repair':repair,
                 'repair_failures':repair_reasons,'aakv':verified,'outcome':outcome}
            f.write(json.dumps(rec,ensure_ascii=False)+'\n'); f.flush(); rows.append(rec)
    del model,tokenizer; gc.collect(); torch.cuda.empty_cache()
    obj={'completed':True,'dataset':ds,'model':'Qwen2.5-7B-Instruct',
         'prompt_sha256':digest(TASK10_CODE),'rows':rows,
         'audit':dict(Counter(x['outcome'] for x in rows))}
    save(final_path,obj); return obj


def embed_second(runtime, clap, generation, out, dim):
    path=out/'second_text_embeddings.pt'; sig=digest(out/'aakv_generation.json')
    if path.exists():
        obj=torch.load(path,map_location='cuda')
        if obj['signature']==sig: return obj
    texts=[]; ids={}; aakv_ix={}; fallback_ix={}
    for row in generation['rows']:
        for field,store in [('aakv',aakv_ix),('fallback',fallback_ix)]:
            text=row[field]
            if text not in ids: ids[text]=len(texts);texts.append(text)
            store[row['path_id']]=ids[text]
    chunks=[]
    for start in tqdm(range(0,len(texts),128),desc='CLAP second text',mininterval=10):
        chunks.append(F.normalize(runtime.get_safe_text_embeddings(clap,texts[start:start+128],'cuda'),dim=-1))
    emb=torch.cat(chunks) if chunks else torch.empty((0,dim),device='cuda')
    obj={'signature':sig,'texts':texts,'embeddings':emb.cpu(),'aakv_ix':aakv_ix,'fallback_ix':fallback_ix}
    torch.save(obj,path); obj['embeddings']=emb; return obj


def calculate_statistics(ranks, comparisons, out):
    r=np.asarray(ranks); hit=(r==1).astype(float); rr=1/r
    contrast=[]; raw_ps=[]; rng=np.random.default_rng(42)
    for x,y in comparisons:
        i=METHODS.index(x);j=METHODS.index(y);dh=100*(hit[:,i]-hit[:,j]);dr=100*(rr[:,i]-rr[:,j])
        boot=np.empty((10000,2))
        for k in range(10000):
            ix=rng.integers(0,len(r),len(r));boot[k]=[dh[ix].mean(),dr[ix].mean()]
        gain=int(np.sum((hit[:,i]==1)&(hit[:,j]==0)));loss=int(np.sum((hit[:,i]==0)&(hit[:,j]==1)))
        p=float(binomtest(gain,gain+loss,.5).pvalue) if gain+loss else 1.
        contrast.append({'comparison':x+'-'+y,'delta_Hit@1_pp':float(dh.mean()),
          'Hit@1_bootstrap95':np.quantile(boot[:,0],[.025,.975]).tolist(),
          'delta_MRR_pp':float(dr.mean()),'MRR_bootstrap95':np.quantile(boot[:,1],[.025,.975]).tolist(),
          'wrong_to_right':gain,'right_to_wrong':loss,'mcnemar_p':p,
          'rank_improved':int(np.sum(r[:,i]<r[:,j])),'rank_worsened':int(np.sum(r[:,i]>r[:,j]))})
        raw_ps.append(p)
    order=np.argsort(raw_ps);holm=np.zeros(len(raw_ps));last=0
    for k,j in enumerate(order):last=max(last,min(1,(len(raw_ps)-k)*raw_ps[j]));holm[j]=last
    for row,p in zip(contrast,holm):row['holm_p']=float(p)
    save(out/'paired_statistics.json',{'comparisons':contrast,'bootstrap':10000,'seed':42})
    return contrast


@torch.inference_mode()
def evaluate(ds,runtime,cfg,paths,generation,out):
    source12=SOURCE12/ds; first=torch.load(source12/'text_embeddings.pt',map_location='cuda')
    label_emb=first['labels'].to('cuda');first_emb=first['evidence'].to('cuda');first_index=first['indices']
    clap=runtime.CLAP(version='2023',use_cuda=True);clap.clap.eval()
    second=embed_second(runtime,clap,generation,out,label_emb.shape[1]);second_emb=second['embeddings'].to('cuda')
    by_class=[[] for _ in paths['classes']]
    for row in generation['rows']:by_class[row['class_id']].append(row)
    dataset=runtime.load_dataset();samples=list(runtime.iter_samples(dataset))
    ranks=[];scores_all=[];orders_all=[];records=[];usage={m:Counter() for m in METHODS}
    base_margins=[]; selected_records=[]
    for si,s in enumerate(tqdm(samples,desc=f'{ds} eval',mininterval=10)):
        audio=torch.load(source12/'audio_cache'/f'{si:06d}.pt',map_location='cuda')
        b=(audio@label_emb.T).squeeze(0);e1=(audio@first_emb.T).squeeze(0);e2=(audio@second_emb.T).squeeze(0)
        top=torch.argsort(b,descending=True)[:K].tolist();alpha=float(np.clip(.4+.4*float(b.max()),.4,.8))
        sorted_b=torch.sort(b,descending=True).values;base_margins.append(float(sorted_b[0]-sorted_b[1]))
        vec={m:b.clone() for m in METHODS};sample_sel={m:[] for m in METHODS}
        for ci in top:
            ids1=first_index[ci]['aakv'];s1=e1[ids1] if ids1 else torch.empty(0,device='cuda')
            for p in P_VALUES:vec[f'1st-P{p}'][ci]=fused(b[ci],s1,alpha,p)[0]
            rows=by_class[ci]
            # Exact Task 14A fallback comparison.
            r1=[x for x in rows if x['kge_rank']<=1];ids=[second['fallback_ix'][x['path_id']] for x in r1]
            vals=e2[ids] if ids else torch.empty(0,device='cuda');joint=torch.cat([s1,GAMMA*vals])
            value,keep=fused(b[ci],joint,alpha,5);vec['Fallback-M1-P5'][ci]=value
            sample_sel['Fallback-M1-P5'] += [r1[int(k)-len(s1)]['path_id'] for k in keep.tolist() if int(k)>=len(s1)]
            for m in M_VALUES:
                rm=[x for x in rows if x['kge_rank']<=m];ids=[second['aakv_ix'][x['path_id']] for x in rm]
                vals=e2[ids] if ids else torch.empty(0,device='cuda');joint=torch.cat([s1,GAMMA*vals])
                for p in P_VALUES:
                    name=f'AAKV-M{m}-P{p}';value,keep=fused(b[ci],joint,alpha,p);vec[name][ci]=value
                    selected=[rm[int(k)-len(s1)] for k in keep.tolist() if int(k)>=len(s1)]
                    sample_sel[name] += [x['path_id'] for x in selected]
                    usage[name]['h2_offered'] += len(rm);usage[name]['h2_selected'] += len(selected)
        orders=torch.stack([torch.argsort(vec[m],descending=True) for m in METHODS]).cpu().numpy()
        sr=[min(int(np.where(o==y)[0][0])+1 for y in s['true_indices']) for o in orders]
        ranks.append(sr);scores_all.append(torch.stack([vec[m] for m in METHODS]).cpu().numpy());orders_all.append(orders)
        for m in METHODS:
            usage[m]['samples']+=1;usage[m]['samples_h2_selected']+=int(bool(sample_sel[m]))
        selected_records.append(sample_sel)
        records.append({'sample_index':si,'audio_path':s['audio_path'],'true_indices':[int(x) for x in s['true_indices']],
                        'base_margin':base_margins[-1],'topk':top,'alpha':alpha,'ranks':dict(zip(METHODS,sr))})
        if (si+1)%50==0:save(out/'progress.json',{'phase':'evaluation','done':si+1,'total':len(samples)})
    r=np.asarray(ranks);metrics={}
    for j,m in enumerate(METHODS):
        x=r[:,j];metrics[m]={'Hit@1':float(100*np.mean(x<=1)),'Hit@3':float(100*np.mean(x<=3)),
                             'Hit@5':float(100*np.mean(x<=5)),'MRR':float(100*np.mean(1/x))}
    save(out/'metrics.json',metrics)
    with (out/'metrics.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.writer(f);w.writerow(['method','Hit@1','Hit@3','Hit@5','MRR'])
        for m in METHODS:w.writerow([m]+[metrics[m][q] for q in ['Hit@1','Hit@3','Hit@5','MRR']])
    comparisons=[('AAKV-M1-P5','Fallback-M1-P5')]
    comparisons += [(f'AAKV-M{m}-P{p}',f'1st-P{p}') for p in P_VALUES for m in M_VALUES]
    contrasts=calculate_statistics(ranks,comparisons,out)
    # Oracle is post-hoc only and never used by inference.
    oracle=np.min(r,axis=1);oracle_metrics={'Hit@1':float(100*np.mean(oracle<=1)),
      'Hit@3':float(100*np.mean(oracle<=3)),'Hit@5':float(100*np.mean(oracle<=5)),'MRR':float(100*np.mean(1/oracle))}
    chosen=np.argmin(r,axis=1);oracle_pick=dict(Counter(METHODS[int(x)] for x in chosen))
    save(out/'oracle.json',{'analysis_only':True,'metrics':oracle_metrics,'chosen_method_counts':oracle_pick})
    # Confidence-stratified effects use one-hop CLAP margin tertiles.
    margins=np.asarray(base_margins);cuts=np.quantile(margins,[1/3,2/3]);bins=np.digitize(margins,cuts)
    strata=[]
    for x,y in comparisons:
        ix,iy=METHODS.index(x),METHODS.index(y)
        for bi,label in enumerate(['low','medium','high']):
            q=bins==bi;strata.append({'comparison':x+'-'+y,'stratum':label,'n':int(q.sum()),
             'delta_Hit@1_pp':float(100*np.mean((r[q,ix]<=1).astype(float)-(r[q,iy]<=1).astype(float))),
             'delta_MRR_pp':float(100*np.mean(1/r[q,ix]-1/r[q,iy]))})
    save(out/'confidence_strata.json',{'cutpoints':cuts.tolist(),'rows':strata})
    # Selected KGE-rank/relation usage, plus beneficial/harmful sample attribution.
    path_lookup={x['path_id']:x for x in generation['rows']};effects={}
    for x,y in comparisons:
        ix,iy=METHODS.index(x),METHODS.index(y);rank_counter=Counter();rel_counter=Counter();benefit=Counter();harm=Counter()
        for si,sel in enumerate(selected_records):
            for pid in sel[x]:
                pr=path_lookup[pid];rank_counter[pr['kge_rank']]+=1;rel_counter[pr['r2']]+=1
                if r[si,ix]<r[si,iy]:benefit[pr['r2']]+=1
                elif r[si,ix]>r[si,iy]:harm[pr['r2']]+=1
        effects[x+'-'+y]={'selected_kge_rank':dict(rank_counter),'selected_relation':dict(rel_counter),
                          'relation_on_improved_samples':dict(benefit),'relation_on_worsened_samples':dict(harm)}
    save(out/'path_effects.json',effects);save(out/'usage.json',{m:dict(v) for m,v in usage.items()})
    save(out/'samples.json',records)
    np.savez_compressed(out/'predictions.npz',scores=np.asarray(scores_all),orders=np.asarray(orders_all),
                        ranks=r,methods=np.asarray(METHODS),base_margin=margins)
    # Verify the matched frozen baseline exactly.
    old=np.load(source12/'predictions.npz',allow_pickle=True);old_methods=[str(x) for x in old['methods']]
    old_d=old['ranks'][:,old_methods.index('D')]
    assert np.array_equal(old_d,r[:,METHODS.index('1st-P5')]),'1st-P5 rank mismatch against Task12 D'
    save(out/'consistency.json',{'task12_D_equals_1st_P5_ranks':True,
      'nested_candidate_rule':'KGE rank <=1 subset <=3 subset <=5','gamma':GAMMA,'gate':False})
    save(out/'progress.json',{'completed':True,'phase':'complete','done':len(samples),'total':len(samples)})
    print(json.dumps({'metrics':metrics,'oracle':oracle_metrics,'generation':generation['audit'],'path_audit':paths['audit']},indent=2),flush=True)


def main(ds, phase):
    seed_all(42);torch.use_deterministic_algorithms(True);torch.backends.cudnn.benchmark=False
    torch.backends.cudnn.deterministic=True;torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
    out=ROOT/ds;out.mkdir(parents=True,exist_ok=True);frozen=out/'frozen_inputs';frozen.mkdir(exist_ok=True)
    src=SOURCE12/ds
    sources={'runtime.py':src/'frozen_inputs/runtime.py','config.json':src/'frozen_inputs/config.json',
             'triples.json':src/'frozen_inputs/triples.json','aakv_first.json':src/'frozen_inputs/aakv.json',
             'mapping.json':src/'frozen_inputs/mapping.json'}
    hashes={}
    for name,p in sources.items():
        q=frozen/name
        if not q.exists():q.write_bytes(p.read_bytes())
        else:assert digest(q)==digest(p)
        hashes[name]=digest(q)
    cfg=json.loads((frozen/'config.json').read_text());triples=json.loads((frozen/'triples.json').read_text())
    if phase == 'paths':
        runtime=load_module(frozen/'runtime.py','runtime_'+ds)
        build_paths(ds,runtime,cfg,triples,out)
        save(out/'progress.json',{'phase':'paths_complete'})
        return
    paths=json.loads((out/'paths_top5.json').read_text(encoding='utf-8'))
    if phase == 'generate':
        save(out/'progress.json',{'phase':'AAKV_generation','done':0})
        generate_aakv(ds,paths,out)
        return
    generation=json.loads((out/'aakv_generation.json').read_text(encoding='utf-8'))
    runtime=load_module(frozen/'runtime.py','runtime_'+ds)
    save(out/'protocol.json',{'purpose':'Task14A second-edge AAKV text-only comparison and Task14B M2/P potential grid',
      'frozen':{'K':K,'M1':M1,'gamma':GAMMA,'gate':False,'relations':cfg['relations'],'audio_cache':str(src/'audio_cache')},
      'varied':{'M2':M_VALUES,'P_total':P_VALUES},'methods':METHODS,'source_hashes':hashes,
      'Task14A':'Fallback-M1-P5 versus AAKV-M1-P5; only second-hop wording changes',
      'Task14B':'AAKV grid; every second-hop method compared with matched 1st-P baseline',
      'status':'exploratory; no test-set winner may be declared as final hyperparameter'})
    evaluate(ds,runtime,cfg,paths,generation,out)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('dataset');p.add_argument('--phase',choices=['paths','generate','evaluate'],required=True)
    a=p.parse_args();main(a.dataset,a.phase)
