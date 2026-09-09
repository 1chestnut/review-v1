import json
import os
import subprocess
import sys
import time
from pathlib import Path

SOURCE = Path('/data/zkx/zkx/review1/05b_strict-map-k5m3-freeze')
TARGET = Path('/data/zkx/zkx/review1/06_onehop-text-verbalization-audit')
PYTHON = '/home/star/anaconda3/envs/zkx/bin/python'
DATASETS = ['01_ESC50','02_UrbanSound8K','03_FSD50K','04_DCASE17_T4','05_AudioSet','06_TUT2017']

def read_state(root, name):
    path = root/name/'run_status.json'
    return json.loads(path.read_text()) if path.exists() else {'state':'not_started'}

def worker(gpu, name):
    folder = TARGET/name
    env = os.environ.copy(); env['CUDA_VISIBLE_DEVICES'] = str(gpu); env['PYTHONUNBUFFERED'] = '1'
    status = {'dataset':name,'gpu':gpu,'state':'running','started_at':time.strftime('%F %T')}
    (folder/'run_status.json').write_text(json.dumps(status,indent=2))
    with (folder/'run.log').open('a') as log:
        code = subprocess.call([PYTHON,'-u',str(folder/'run_onehop_text_audit.py')],cwd=folder,env=env,stdout=log,stderr=subprocess.STDOUT)
    status.update(state='completed' if code==0 else 'failed',exit_code=code,finished_at=time.strftime('%F %T'))
    (folder/'run_status.json').write_text(json.dumps(status,indent=2))

def scheduler():
    while True:
        source = {n:read_state(SOURCE,n) for n in DATASETS}
        target = {n:read_state(TARGET,n) for n in DATASETS}
        if all(target[n]['state'] in {'completed','failed'} for n in DATASETS): break
        busy = set()
        for item in source.values():
            if item.get('state') in {'running','queued'} and 'gpu' in item: busy.add(int(item['gpu']))
        for item in target.values():
            if item.get('state') in {'running','queued'} and 'gpu' in item: busy.add(int(item['gpu']))
        free = [gpu for gpu in [0,1,2] if gpu not in busy]
        ready = [n for n in DATASETS if source[n].get('state')=='completed' and target[n].get('state')=='not_started']
        for gpu,name in zip(free,ready):
            (TARGET/name/'run_status.json').write_text(json.dumps({'dataset':name,'gpu':gpu,'state':'queued'},indent=2))
            with (TARGET/f'dynamic_gpu{gpu}_{name}.log').open('a') as log:
                subprocess.Popen([PYTHON,str(Path(__file__).resolve()),'worker',str(gpu),name],cwd=TARGET,
                                 stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
        snapshot={'source':{n:source[n].get('state') for n in DATASETS},
                  'target':{n:read_state(TARGET,n).get('state') for n in DATASETS},
                  'busy_gpus':sorted(busy),'checked_at':time.strftime('%F %T')}
        (TARGET/'dynamic_scheduler_status.json').write_text(json.dumps(snapshot,indent=2))
        time.sleep(10)

if __name__=='__main__':
    worker(int(sys.argv[2]),sys.argv[3]) if len(sys.argv)==4 and sys.argv[1]=='worker' else scheduler()
