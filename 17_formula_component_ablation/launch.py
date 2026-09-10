import os,subprocess,sys
from pathlib import Path
ROOT=Path('/data/zkx/zkx/review1/17_formula_component_ablation');PY='/home/star/anaconda3/envs/zkx/bin/python'
groups={0:['01_ESC50','04_DCASE17_T4'],1:['02_UrbanSound8K','06_TUT2017'],2:['03_FSD50K','05_AudioSet']};procs=[]
for gpu,datasets in groups.items():
 log=(ROOT/f'gpu{gpu}.log').open('a',buffering=1);cmd=' && '.join(f'{PY} -u {ROOT}/run.py {d}' for d in datasets)
 env=os.environ.copy();env['CUDA_VISIBLE_DEVICES']=str(gpu);procs.append(subprocess.Popen(['bash','-lc',cmd],stdout=log,stderr=subprocess.STDOUT,env=env))
for p in procs:
 if p.wait()!=0:sys.exit(p.returncode)
