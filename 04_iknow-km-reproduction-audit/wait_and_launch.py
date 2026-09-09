import json,os,subprocess,sys,time
from pathlib import Path
ROOT=Path('/data/zkx/zkx/review1/04_iknow-km-reproduction-audit')
PREV=Path('/data/zkx/zkx/review1/03_full-second-hop-pilot')
STRICT=Path('/data/zkx/zkx/review1/02clap-iknow-strict-map-v2')
Q={0:['05_AudioSet','04_DCASE17_T4'],1:['03_FSD50K','02_UrbanSound8K'],2:['01_ESC50','06_TUT2017']}
def done(folder):
 try:return bool(json.loads((folder/'results'/'exploratory_results.json').read_text()).get('completed'))
 except:return False
def strict_done(folder):
 try:return bool(json.loads((folder/'results'/'clap_iknow_results.json').read_text()).get('completed'))
 except:return False
def worker(gpu):
 env=os.environ.copy();env['CUDA_VISIBLE_DEVICES']=str(gpu);env['PYTHONUNBUFFERED']='1'
 for name in Q[gpu]:
  d=ROOT/name;st={'dataset':name,'gpu':gpu,'state':'running','started_at':time.strftime('%F %T')}
  with (d/'run.log').open('a') as log:
   p=subprocess.Popen([sys.executable,'-u',str(d/'run_km_audit.py')],cwd=d,env=env,stdout=log,stderr=subprocess.STDOUT);st['pid']=p.pid;(d/'run_status.json').write_text(json.dumps(st,indent=2));code=p.wait()
  st.update(state='completed' if code==0 else 'failed',exit_code=code,finished_at=time.strftime('%F %T'));(d/'run_status.json').write_text(json.dumps(st,indent=2))
def monitor():
 launched=set()
 while len(launched)<3:
  state={n:(done(PREV/n) and strict_done(STRICT/n)) for q in Q.values() for n in q}
  for gpu,q in Q.items():
   # Strict US8K was moved to physical GPU2 to use an idle card. Do not let
   # task04 overlap it merely because US8K belongs to the nominal GPU1 queue.
   physical_gpu_free = not (gpu == 2 and not strict_done(STRICT/'02_UrbanSound8K'))
   if gpu in launched or not physical_gpu_free or not all(state[n] for n in q):continue
   for n in q:(ROOT/n/'run_status.json').write_text(json.dumps({'state':'queued','gpu':gpu},indent=2))
   with (ROOT/f'gpu{gpu}_queue.log').open('a') as log:subprocess.Popen([sys.executable,str(Path(__file__).resolve()),'worker',str(gpu)],stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
   launched.add(gpu)
  (ROOT/'launch_status.json').write_text(json.dumps({'state':'partially_launched' if launched else 'waiting_for_03','launched_gpus':sorted(launched),'previous_completed':state,'checked_at':time.strftime('%F %T')},indent=2))
  if len(launched)<3:time.sleep(30)
if __name__=='__main__':worker(int(sys.argv[2])) if len(sys.argv)==3 else monitor()
