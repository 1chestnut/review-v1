#!/usr/bin/env python3
"""One-hop iKnow reproduction audit over K={5,10,15}, M={1,3,5}."""
import hashlib, importlib.util, json, math, os, time, warnings
from collections import OrderedDict
from pathlib import Path
import numpy as np
import torch
import torch.nn.functional as F
from pykeen.triples import TriplesFactory
from tqdm import tqdm

HERE=Path(__file__).resolve().parent
CFG=json.loads((HERE/'config.json').read_text())
RESULTS=HERE/'results'; CACHE=HERE/'cache'
KS=(5,10,15); MS=(1,3,5)

def load_runtime():
    s=importlib.util.spec_from_file_location('frozen01',HERE/'iknow_runtime.py')
    m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def metric(r):
    x=np.asarray(r,float)
    return {'Hit@1':float(100*np.mean(x<=1)),'Hit@3':float(100*np.mean(x<=3)),
            'Hit@5':float(100*np.mean(x<=5)),'MRR':float(100*np.mean(1/x))}

def rank(scores,truth):
    order=torch.argsort(scores,descending=True).cpu().tolist()
    return min(order.index(int(t))+1 for t in truth)

def lme(base,evidence,scale):
    values=torch.cat([base.reshape(1),evidence])
    return (torch.logsumexp(scale*values,0)-math.log(values.numel()))/scale

def static_cache(base,kge,factory,labels,kg_classes,clap,device):
    CACHE.mkdir(parents=True,exist_ok=True)
    signature={'dataset':CFG['dataset'],'labels':labels,'kg_classes':kg_classes,
               'relations':CFG['relations'],'max_m':max(MS),'text':'class_name, tail',
               'mapping_runtime_sha256':hashlib.sha256((HERE/'iknow_runtime.py').read_bytes()).hexdigest()}
    sig=hashlib.sha256(json.dumps(signature,sort_keys=True).encode()).hexdigest()
    kp=CACHE/'knowledge.json'; ep=CACHE/'text_embeddings.pt'
    if kp.exists() and ep.exists():
        k=json.loads(kp.read_text());e=torch.load(ep,map_location='cpu')
        if k.get('signature_hash')==sig and e.get('signature_hash')==sig:
            return k,e['label'].to(device),e['evidence'].to(device),e['indices']
    base.TOP_M=max(MS);get_tails=base.build_tail_predictor(kge,factory)
    valid=[r for r in CFG['relations'] if r in factory.relation_to_id]
    candidates={str(x).lower().strip() for x in labels}
    all_text=[];text_id={};indices=[];classes=[]
    audit={'mapped_classes':0,'unmapped_classes':0,'queries':0,'empty_queries':0}
    for label,kg_class in zip(labels,kg_classes):
        head=base.get_kg_entity(kg_class);query=base.resolve_head_query(head,factory)
        per_relation=[]
        if query not in factory.entity_to_id:
            audit['unmapped_classes']+=1; per_relation=[[] for _ in valid]
        else:
            audit['mapped_classes']+=1
            for rel in valid:
                tails=get_tails(head,rel);audit['queries']+=1
                if not tails:audit['empty_queries']+=1
                per_relation.append([str(t) for t in tails])
        by_m={}
        for m in MS:
            unique=OrderedDict()
            for tails in per_relation:
                for tail in tails[:m]:
                    norm=tail.lower().strip()
                    if norm==str(label).lower().strip() or norm in candidates:continue
                    unique.setdefault(norm,f'{label}, {tail}')
            ids=[]
            for text in unique.values():
                if text not in text_id:text_id[text]=len(all_text);all_text.append(text)
                ids.append(text_id[text])
            by_m[str(m)]=ids
        indices.append(by_m);classes.append({'label':label,'kg_class':kg_class,'head':head,'tails_by_relation':per_relation})
    label_emb=F.normalize(base.get_safe_text_embeddings(clap,labels,device),dim=-1)
    chunks=[]
    for i in range(0,len(all_text),128):
        chunks.append(F.normalize(base.get_safe_text_embeddings(clap,all_text[i:i+128],device),dim=-1))
    evidence=torch.cat(chunks) if chunks else torch.empty((0,label_emb.shape[1]),device=device)
    knowledge={'signature':signature,'signature_hash':sig,'valid_relations':valid,'classes':classes,'texts':all_text,'audit':audit}
    kp.write_text(json.dumps(knowledge,ensure_ascii=False,indent=2))
    torch.save({'signature_hash':sig,'label':label_emb.cpu(),'evidence':evidence.cpu(),'indices':indices},ep)
    return knowledge,label_emb,evidence,indices

@torch.no_grad()
def main():
    RESULTS.mkdir(parents=True,exist_ok=True)
    base=load_runtime();device=base.DEVICE
    clap=base.CLAP(version='2023',use_cuda=torch.cuda.is_available())
    with warnings.catch_warnings():
        warnings.simplefilter('ignore');kge=torch.load(os.path.join(base.KGE_MODEL_DIR,'trained_model.pkl'),map_location=device)
    kge.eval();factory=TriplesFactory.from_path(base.TRAIN_TRIPLES_PATH)
    data=base.load_dataset();labels=list(data['label_classes']);kg_classes=list(data['kg_classes']);samples=list(base.iter_samples(data))
    knowledge,label_emb,evidence_emb,indices=static_cache(base,kge,factory,labels,kg_classes,clap,device)
    names=['CLAP']+[f'iKnow-K{k}-M{m}' for k in KS for m in MS]
    ranks={x:[] for x in names};rows=[];skipped=0;scale=float(CFG['logit_scale'])
    for n,sample in enumerate(tqdm(samples,desc=CFG['dataset'],mininterval=10)):
        if not os.path.exists(sample['audio_path']) or not sample['true_indices']:
            skipped+=1;continue
        try:
            audio=F.normalize(base.to_tensor(clap.get_audio_embeddings([sample['audio_path']])).to(device).float(),dim=-1)
        except Exception:
            skipped+=1;continue
        base_scores=(audio@label_emb.T).squeeze(0)
        evidence_scores=(audio@evidence_emb.T).squeeze(0)
        order=torch.argsort(base_scores,descending=True).tolist()
        sample_ranks={'CLAP':rank(base_scores,sample['true_indices'])}
        for k in KS:
            top=order[:min(k,len(labels))]
            for m in MS:
                scores=base_scores.clone()
                for j in top:
                    ids=indices[j][str(m)]
                    if ids:scores[j]=lme(base_scores[j],evidence_scores[ids],scale)
                name=f'iKnow-K{k}-M{m}';sample_ranks[name]=rank(scores,sample['true_indices'])
        for name in names:ranks[name].append(int(sample_ranks[name]))
        rows.append({'sample_index':n,'audio_path':sample['audio_path'],'true_indices':[int(x) for x in sample['true_indices']],'ranks':sample_ranks})
        if len(rows)%20==0:
            (RESULTS/'progress.json').write_text(json.dumps({'processed':len(rows),'total':len(samples),'skipped':skipped}))
    metrics={name:metric(values) for name,values in ranks.items()}
    gains={}
    for name in names[1:]:
        gains[name]={x:metrics[name][x]-metrics['CLAP'][x] for x in ('Hit@1','Hit@3','Hit@5','MRR')}
    protocol={'purpose':'reproduction calibration for unpublished iKnow K/M; not Ours tuning',
              'depth':1,'mapping':'01 original runtime','relations':CFG['relations'],
              'k_values':list(KS),'m_values':list(MS),'knowledge_text':'class_name, tail',
              'aggregation':'joint evidence-count-normalized LME100','other_modules':False,
              'selection':'no automatic winner; compare paper-relative gains only after all datasets finish'}
    result={'completed':True,'dataset':CFG['dataset'],'evaluated_samples':len(rows),'skipped':skipped,
            'protocol':protocol,'metrics':metrics,'gains_over_clap':gains,'knowledge_audit':knowledge['audit'],'samples':rows,'created_at':time.strftime('%Y-%m-%d %H:%M:%S')}
    (RESULTS/'km_audit_results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    lines=['method,Hit@1,Hit@3,Hit@5,MRR,delta_Hit@1,delta_MRR']
    for name in names:
        z=metrics[name];g=gains.get(name,{'Hit@1':0,'MRR':0})
        lines.append(f"{name},{z['Hit@1']:.8f},{z['Hit@3']:.8f},{z['Hit@5']:.8f},{z['MRR']:.8f},{g['Hit@1']:.8f},{g['MRR']:.8f}")
    (RESULTS/'km_audit_table.csv').write_text('\n'.join(lines)+'\n')
    print(json.dumps(metrics,indent=2),flush=True)

if __name__=='__main__':main()
