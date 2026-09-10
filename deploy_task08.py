#!/usr/bin/env python3
import json, shutil
from pathlib import Path

root=Path('/data/zkx/zkx/review1')
source=root/'06_onehop-text-verbalization-audit'
target=root/'08_unlabeled-verbalization-router'
build=root/'task08_stage'
target.mkdir(exist_ok=True)
for filename in ['dynamic_scheduler.py','PROTOCOL.md']:
    shutil.copy2(build/filename,target/filename)
for folder in sorted(source.glob('[0-9][0-9]_*')):
    out=target/folder.name; out.mkdir(exist_ok=True)
    shutil.copy2(build/'run_unlabeled_router.py',out/'run_unlabeled_router.py')
    shutil.copy2(folder/'iknow_runtime.py',out/'iknow_runtime.py')
    cfg=json.loads((folder/'config.json').read_text())
    cfg['task06_cache']=str(folder/'cache')
    (out/'config.json').write_text(json.dumps(cfg,indent=2)+'\n')
print(target)
