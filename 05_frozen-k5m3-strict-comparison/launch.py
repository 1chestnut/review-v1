import json,os,subprocess,sys,time
from pathlib import Path
ROOT=Path('/data/zkx/zkx/review1/05_frozen-k5m3-strict-comparison')
Q={0:['05_AudioSet','04_DCASE17_T4'],1:['03_FSD50K','02_UrbanSound8K'],2:['01_ESC50','06_TUT2017']}
def worker(gpu):
 env=os.environ.copy();env['CUDA_VISIBLE_DEVICES']=str(gpu);env['PYTHONUNBUFFERED']='1'
 for name in Q[gpu]:
  d=ROOT/name;st={'dataset':name,'gpu':gpu,'state':'running','started_at':time.strftime('%F %T')}
  with (d/'run.log').open('a') as log:
   p=subprocess.Popen([sys.executable,'-u',str(d/'run_comparison.py')],cwd=d,env=env,stdout=log,stderr=subprocess.STDOUT);st['pid']=p.pid;(d/'run_status.json').write_text(json.dumps(st,indent=2));code=p.wait()
  st.update(state='completed' if code==0 else 'failed',exit_code=code,finished_at=time.strftime('%F %T'));(d/'run_status.json').write_text(json.dumps(st,indent=2))
def launch():
 for gpu,q in Q.items():
  for name in q:(ROOT/name/'run_status.json').write_text(json.dumps({'state':'queued','gpu':gpu},indent=2))
  with (ROOT/f'gpu{gpu}_queue.log').open('a') as log:subprocess.Popen([sys.executable,str(Path(__file__).resolve()),'worker',str(gpu)],stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
 (ROOT/'launch_status.json').write_text(json.dumps({'state':'all_gpu_queues_launched','launched_at':time.strftime('%F %T'),'queues':Q},indent=2))
if __name__=='__main__':worker(int(sys.argv[2])) if len(sys.argv)==3 else launch()
