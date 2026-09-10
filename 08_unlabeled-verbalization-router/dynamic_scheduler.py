import json, os, subprocess, sys, time
from pathlib import Path

TASK06=Path('/data/zkx/zkx/review1/06_onehop-text-verbalization-audit')
TARGET=Path('/data/zkx/zkx/review1/08_unlabeled-verbalization-router')
PYTHON='/home/star/anaconda3/envs/zkx/bin/python'
DATASETS=['01_ESC50','02_UrbanSound8K','03_FSD50K','04_DCASE17_T4','05_AudioSet','06_TUT2017']

def state(root,name):
    p=root/name/'run_status.json'
    return json.loads(p.read_text()) if p.exists() else {'state':'not_started'}

def worker(gpu,name):
    folder=TARGET/name; status={'dataset':name,'gpu':gpu,'state':'running','started_at':time.strftime('%F %T')}
    (folder/'run_status.json').write_text(json.dumps(status,indent=2))
    env=os.environ.copy(); env['CUDA_VISIBLE_DEVICES']=str(gpu); env['PYTHONUNBUFFERED']='1'
    with (folder/'run.log').open('a') as log:
        code=subprocess.call([PYTHON,'-u',str(folder/'run_unlabeled_router.py')],cwd=folder,env=env,stdout=log,stderr=subprocess.STDOUT)
    status.update(state='completed' if code==0 else 'failed',exit_code=code,finished_at=time.strftime('%F %T'))
    (folder/'run_status.json').write_text(json.dumps(status,indent=2))

def scheduler():
    while True:
        target={n:state(TARGET,n) for n in DATASETS}
        if all(x.get('state') in {'completed','failed'} for x in target.values()): break
        # Protect GPUs occupied by any real compute process, including other users.
        out=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid','--format=csv,noheader'],text=True)
        uuids=[x.strip() for x in out.splitlines() if x.strip()]
        gpu_lines=subprocess.check_output(['nvidia-smi','--query-gpu=index,uuid','--format=csv,noheader'],text=True).splitlines()
        busy={int(line.split(',')[0]) for line in gpu_lines if line.split(',',1)[1].strip() in uuids}
        ready=[n for n in DATASETS if state(TASK06,n).get('state')=='completed' and target[n].get('state')=='not_started']
        free=[g for g in [0,1,2] if g not in busy]
        for gpu,name in zip(free,ready):
            (TARGET/name/'run_status.json').write_text(json.dumps({'dataset':name,'gpu':gpu,'state':'queued'},indent=2))
            subprocess.Popen([PYTHON,str(Path(__file__).resolve()),'worker',str(gpu),name],cwd=TARGET,
                             stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True)
        (TARGET/'scheduler_status.json').write_text(json.dumps({'task06':{n:state(TASK06,n).get('state') for n in DATASETS},
          'task08':{n:state(TARGET,n).get('state') for n in DATASETS},'busy_gpus':sorted(busy),'checked_at':time.strftime('%F %T')},indent=2))
        time.sleep(10)

if __name__=='__main__':
    worker(int(sys.argv[2]),sys.argv[3]) if len(sys.argv)==4 and sys.argv[1]=='worker' else scheduler()
