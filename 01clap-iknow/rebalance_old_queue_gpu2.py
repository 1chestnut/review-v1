import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT=Path('/data/zkx/zkx/review1/clap-iknow')
env=os.environ.copy();env['CUDA_VISIBLE_DEVICES']='2';env['PYTHONUNBUFFERED']='1'
for name in ['02_UrbanSound8K','04_DCASE17_T4']:
    folder=ROOT/name
    status={'dataset':name,'gpu':2,'state':'running','started_at':time.strftime('%Y-%m-%d %H:%M:%S'),'queue':'rebalanced_to_free_gpu2'}
    with (folder/'run.log').open('a') as log:
        process=subprocess.Popen([sys.executable,'-u',str(folder/'run_clap_iknow.py')],cwd=folder,env=env,stdout=log,stderr=subprocess.STDOUT)
        status['pid']=process.pid
        (folder/'run_status.json').write_text(json.dumps(status,indent=2))
        code=process.wait()
    status.update(state='completed' if code==0 else 'failed',exit_code=code,finished_at=time.strftime('%Y-%m-%d %H:%M:%S'))
    (folder/'run_status.json').write_text(json.dumps(status,indent=2))
