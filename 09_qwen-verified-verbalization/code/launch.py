#!/usr/bin/env python3
import json, os, subprocess, time
from pathlib import Path

ROOT=Path('/data/zkx/zkx/review1/09_qwen-verified-verbalization')
JOBS={0:['01_ESC50','04_DCASE17_T4'],1:['02_UrbanSound8K','06_TUT2017'],2:['03_FSD50K','05_AudioSet']}
PYTHON='/home/star/anaconda3/envs/zkx/bin/python'

def main():
    pids=[]
    for gpu,datasets in JOBS.items():
        log=ROOT/f'gpu{gpu}_queue.log'
        cmd='set -e\n'+'\n'.join(
            f"echo '[START] {ds} '$(date); {PYTHON} {ROOT/'code/run_qwen_verified.py'} {ds}; echo '[DONE] {ds} '$(date)"
            for ds in datasets)
        env=os.environ.copy(); env['CUDA_VISIBLE_DEVICES']=str(gpu)
        fh=open(log,'a',buffering=1)
        proc=subprocess.Popen(['bash','-lc',cmd],stdout=fh,stderr=subprocess.STDOUT,env=env,start_new_session=True)
        pids.append({'gpu':gpu,'datasets':datasets,'pid':proc.pid,'log':str(log)})
    (ROOT/'launch_status.json').write_text(json.dumps({'started_at':time.strftime('%F %T'),'workers':pids},indent=2))
    print(json.dumps(pids,indent=2))
if __name__=='__main__': main()
