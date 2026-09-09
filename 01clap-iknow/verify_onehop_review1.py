import ast
import json
from collections import OrderedDict
from pathlib import Path
from types import SimpleNamespace
import numpy as np
import torch

root=Path('/data/zkx/zkx/review1/clap-iknow')
sources=json.loads((root/'old_onehop_reference.json').read_text())
reports={}
for folder in sorted(root.glob('0*')):
    cfg=json.loads((folder/'config.json').read_text())
    tree=ast.parse((folder/'run_clap_iknow.py').read_text())
    pool=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='normalized_lse')
    main=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main')
    loop=next(n for n in ast.walk(main) if isinstance(n,ast.For) and isinstance(n.target,ast.Name) and n.target.id=='class_index')
    def evidence(clap,audio,prompts):
        return torch.tensor([0.1+sum(map(ord,p))%43/100 for p in prompts])
    env={'torch':torch,'np':np,'OrderedDict':OrderedDict,'LOGIT_SCALE':cfg['logit_scale'],'score_prompt_list':evidence}
    exec(sources[folder.name],env)
    exec(compile(ast.Module(body=[pool],type_ignores=[]),'pool','exec'),env)
    for case in range(20):
        labels=['class'+str(i) for i in range(20)]
        scores=torch.linspace(-.2,.7,20).roll(case)
        indices=torch.argsort(scores,descending=True)[:cfg['top_k']].tolist()
        def tails(head,relation):
            i=int(head[5:])
            return [] if i%4==0 else [head,'class0','tail'+str(i%3),'tail'+str(i%3),'other']
        env['get_kg_entity']=lambda x:x
        expected,count=env['run_iknow'](None,None,scores,indices,labels,labels,set(labels),cfg['relations'],tails)
        base=SimpleNamespace(get_kg_entity=lambda x:x,resolve_head_query=lambda h,f:h,score_prompt_list=evidence)
        env.update(base=base,labels=labels,kg_classes=labels,factory=SimpleNamespace(entity_to_id={x:i for i,x in enumerate(labels)}),top_indices=indices,clap_scores=scores,iknow_scores=scores.clone(),class_labels_set=set(labels),valid_relations=cfg['relations'],get_tails=tails,clap=None,audio=None,logit_scale=cfg['logit_scale'],sample_prompt_count=0,audit={'mapped_topk':0,'unmapped_topk':0,'valid_relation_queries':0,'empty_relation_queries':0})
        exec(compile(ast.Module(body=[loop],type_ignores=[]),'actual_new_loop','exec'),env)
        assert torch.equal(expected,env['iknow_scores'])
        assert count==env['sample_prompt_count']
    reports[folder.name]={'synthetic_cases':20,'exact_scores_and_prompt_counts':True,'scope':'same synthetic evidence; real audio rerun still required'}
(root/'onehop_logic_test.json').write_text(json.dumps(reports,indent=2))
print(json.dumps(reports,indent=2))
