import json,os,subprocess,sys,time
from pathlib import Path
ROOT=Path('/data/zkx/zkx/review1/14_aakv_mp_potential')
QUEUES={0:['05_AudioSet'],1:['03_FSD50K','01_ESC50'],2:['02_UrbanSound8K','04_DCASE17_T4','06_TUT2017']}
def worker(gpu):
 env=os.environ.copy();env['CUDA_VISIBLE_DEVICES']=str(gpu);env['PYTHONUNBUFFERED']='1'
 for ds in QUEUES[gpu]:
  folder=ROOT/ds;folder.mkdir(parents=True,exist_ok=True)
  status={'state':'running','dataset':ds,'gpu':gpu,'started_at':time.strftime('%F %T')}
  save=folder/'run_status.json';save.write_text(json.dumps(status,indent=2))
  with (folder/'run.log').open('a') as log:
   code=0
   for phase in ['paths','generate','evaluate']:
    status['phase']=phase;save.write_text(json.dumps(status,indent=2))
    p=subprocess.Popen([sys.executable,'-u',str(ROOT/'run.py'),ds,'--phase',phase],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT)
    status['pid']=p.pid;save.write_text(json.dumps(status,indent=2));code=p.wait()
    if code:break
  status.update(state='completed' if code==0 else 'failed',exit_code=code,finished_at=time.strftime('%F %T'))
  save.write_text(json.dumps(status,indent=2))
if __name__=='__main__':
 if len(sys.argv)==3:worker(int(sys.argv[2]))
 else:
  for gpu,queue in QUEUES.items():
   for ds in queue:
    f=ROOT/ds;f.mkdir(parents=True,exist_ok=True);(f/'run_status.json').write_text(json.dumps({'state':'queued','gpu':gpu},indent=2))
   with (ROOT/f'gpu{gpu}.log').open('a') as log:
    subprocess.Popen([sys.executable,str(ROOT/'launch.py'),'worker',str(gpu)],stdin=subprocess.DEVNULL,
                     stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
