import ast
import importlib.util
import json
from pathlib import Path
import numpy as np
import torch
from collections import OrderedDict

root = Path('/data/zkx/zkx/review1/clap-iknow')
reports = {}
for folder in sorted(root.glob('0*')):
    spec=importlib.util.spec_from_file_location('rt',folder/'iknow_runtime.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    data=module.load_dataset();samples=list(module.iter_samples(data))
    missing=[s['audio_path'] for s in samples if not Path(s['audio_path']).is_file()]
    empty=sum(not s['true_indices'] for s in samples)
    paths={n:str(v) for n,v in vars(module).items() if n in ['CLAP_WEIGHTS_PATH','TRAIN_TRIPLES_PATH','GPT2_LOCAL_PATH','ROBERTA_LOCAL_PATH']}
    report={'rows':len(samples),'classes':len(data['label_classes']),'missing_audio':len(missing),'empty_labels':empty,'required_paths_exist':{k:Path(v).exists() for k,v in paths.items()},'paths':paths}
    reports[folder.name]=report
    print(folder.name,json.dumps(report),flush=True)
    assert not missing and not empty and all(report['required_paths_exist'].values()), report
(root/'data_preflight.json').write_text(json.dumps(reports,indent=2))
