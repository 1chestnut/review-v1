import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT=Path(__file__).resolve().parent
QUEUES={0:['05_AudioSet','04_DCASE17_T4'],1:['03_FSD50K','02_UrbanSound8K'],2:['01_ESC50','06_TUT2017']}
def worker(gpu):
    env=os.environ.copy();env['CUDA_VISIBLE_DEVICES']=str(gpu);env['PYTHONUNBUFFERED']='1'
    for name in QUEUES[gpu]:
        folder=ROOT/name
        status={'dataset':name,'gpu':gpu,'state':'running','started_at':time.strftime('%Y-%m-%d %H:%M:%S')}
        with (folder/'run.log').open('a') as log:
            process=subprocess.Popen([sys.executable,'-u',str(folder/'run_clap_iknow.py')],cwd=folder,env=env,stdout=log,stderr=subprocess.STDOUT)
            status['pid']=process.pid
            (folder/'run_status.json').write_text(json.dumps(status,indent=2))
            code=process.wait()
        status.update(state='completed' if code==0 else 'failed',exit_code=code,finished_at=time.strftime('%Y-%m-%d %H:%M:%S'))
        (folder/'run_status.json').write_text(json.dumps(status,indent=2))
if __name__=='__main__':
    if len(sys.argv)>1:worker(int(sys.argv[1]))
    else:
        for gpu,names in QUEUES.items():
            for name in names:
                (ROOT/name/'run_status.json').write_text(json.dumps({'state':'queued','gpu':gpu},indent=2))
            with (ROOT/f'gpu{gpu}_queue.log').open('a') as log:
                p=subprocess.Popen([sys.executable,str(Path(__file__).resolve()),str(gpu)],stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
            print(f'GPU {gpu}: queue PID {p.pid}: {names}',flush=True)
