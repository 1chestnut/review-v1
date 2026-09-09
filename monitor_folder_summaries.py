import json, subprocess, sys, time
from pathlib import Path

root=Path('/data/zkx/zkx/review1/05_frozen-k5m3-strict-comparison')
names=['01_ESC50','02_UrbanSound8K','03_FSD50K','04_DCASE17_T4','05_AudioSet','06_TUT2017']
while True:
    subprocess.run([sys.executable,'/data/zkx/zkx/review1/build_folder_summaries.py'])
    complete=[]
    for name in names:
        try:complete.append(bool(json.loads((root/name/'results'/'exploratory_results.json').read_text()).get('completed')))
        except:complete.append(False)
    if all(complete):break
    time.sleep(60)
