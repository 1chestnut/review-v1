import json
import os
import subprocess
import time
from pathlib import Path

SOURCE = Path('/data/zkx/zkx/review1/05b_strict-map-k5m3-freeze')
TARGET = Path('/data/zkx/zkx/review1/06_onehop-text-verbalization-audit')
PYTHON = '/home/star/anaconda3/envs/zkx/bin/python'
GROUPS = {
    0: ['05_AudioSet', '04_DCASE17_T4'],
    1: ['03_FSD50K', '02_UrbanSound8K'],
    2: ['01_ESC50', '06_TUT2017'],
}

def source_state(name):
    path = SOURCE / name / 'run_status.json'
    return json.loads(path.read_text()).get('state') if path.exists() else 'missing'

def target_state(name):
    path = TARGET / name / 'run_status.json'
    return json.loads(path.read_text()).get('state') if path.exists() else 'not_started'

launched = set()
while len(launched) < len(GROUPS):
    snapshot = {}
    for gpu, names in GROUPS.items():
        source_states = [source_state(name) for name in names]
        target_states = [target_state(name) for name in names]
        snapshot[str(gpu)] = {'datasets': names, 'source': source_states, 'target': target_states}
        if any(state == 'failed' for state in source_states):
            snapshot[str(gpu)]['pipeline'] = 'blocked_source_failed'
            launched.add(gpu)
            continue
        already_started = any(state in {'queued', 'running', 'completed'} for state in target_states)
        if already_started:
            snapshot[str(gpu)]['pipeline'] = 'already_started'
            launched.add(gpu)
            continue
        if all(state == 'completed' for state in source_states):
            env = os.environ.copy()
            env['PYTHONUNBUFFERED'] = '1'
            for name in names:
                (TARGET / name / 'run_status.json').write_text(json.dumps({'state': 'queued', 'gpu': gpu}, indent=2))
            log = (TARGET / f'gpu{gpu}_queue.log').open('a')
            subprocess.Popen([PYTHON, str(TARGET / 'launch.py'), 'worker', str(gpu)],
                             cwd=TARGET, env=env, stdin=subprocess.DEVNULL,
                             stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
            snapshot[str(gpu)]['pipeline'] = 'launched'
            launched.add(gpu)
        else:
            snapshot[str(gpu)]['pipeline'] = 'waiting_for_own_05b_queue'
    (TARGET / 'wait_status.json').write_text(json.dumps({
        'mode': 'per_gpu_pipeline', 'groups': snapshot, 'checked_at': time.strftime('%F %T')
    }, indent=2))
    if len(launched) < len(GROUPS):
        time.sleep(15)

(TARGET / 'wait_status.json').write_text(json.dumps({
    'mode': 'per_gpu_pipeline', 'state': 'all_gpu_groups_dispatched_or_blocked',
    'finished_at': time.strftime('%F %T')
}, indent=2))
