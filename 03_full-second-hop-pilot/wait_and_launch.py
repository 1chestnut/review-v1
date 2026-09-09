import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path('/data/zkx/zkx/review1/03_full-second-hop-pilot')
PREVIOUS = Path('/data/zkx/zkx/review1/02clap-iknow-strict-map-v2')
QUEUES = {
    0: ['05_AudioSet', '04_DCASE17_T4'],
    1: ['03_FSD50K', '02_UrbanSound8K'],
    2: ['01_ESC50', '06_TUT2017'],
}


def complete(folder):
    try:
        return bool(json.loads((folder / 'results' / 'clap_iknow_results.json').read_text()).get('completed'))
    except (FileNotFoundError, json.JSONDecodeError):
        return False


def worker(gpu):
    env = os.environ.copy()
    env['CUDA_VISIBLE_DEVICES'] = str(gpu)
    env['PYTHONUNBUFFERED'] = '1'
    for name in QUEUES[gpu]:
        folder = ROOT / name
        status = {'dataset': name, 'gpu': gpu, 'state': 'running',
                  'started_at': time.strftime('%Y-%m-%d %H:%M:%S')}
        with (folder / 'run.log').open('a') as log:
            p = subprocess.Popen([sys.executable, '-u', str(folder / 'run_exploratory.py')],
                                 cwd=folder, env=env, stdout=log,
                                 stderr=subprocess.STDOUT)
            status['pid'] = p.pid
            (folder / 'run_status.json').write_text(json.dumps(status, indent=2))
            code = p.wait()
        status.update(state='completed' if code == 0 else 'failed', exit_code=code,
                      finished_at=time.strftime('%Y-%m-%d %H:%M:%S'))
        (folder / 'run_status.json').write_text(json.dumps(status, indent=2))


def monitor():
    launched = set()
    while len(launched) < 3:
        prior = {name: complete(PREVIOUS / name)
                 for queue in QUEUES.values() for name in queue}
        for gpu, queue in QUEUES.items():
            if gpu in launched or not all(prior[name] for name in queue):
                continue
            for name in queue:
                (ROOT / name / 'run_status.json').write_text(
                    json.dumps({'state': 'queued', 'gpu': gpu}, indent=2))
            with (ROOT / f'gpu{gpu}_queue.log').open('a') as log:
                subprocess.Popen([sys.executable, str(Path(__file__).resolve()),
                                  'worker', str(gpu)], stdin=subprocess.DEVNULL,
                                 stdout=log, stderr=subprocess.STDOUT,
                                 start_new_session=True)
            launched.add(gpu)
        (ROOT / 'launch_status.json').write_text(json.dumps({
            'state': 'partially_launched' if launched else 'waiting_for_02',
            'launched_gpus': sorted(launched), 'previous_completed': prior,
            'checked_at': time.strftime('%Y-%m-%d %H:%M:%S')}, indent=2))
        if len(launched) < 3:
            time.sleep(30)
    (ROOT / 'launch_status.json').write_text(json.dumps({
        'state': 'all_gpu_queues_launched', 'launched_gpus': sorted(launched),
        'launched_at': time.strftime('%Y-%m-%d %H:%M:%S')}, indent=2))


if __name__ == '__main__':
    if len(sys.argv) == 3 and sys.argv[1] == 'worker':
        worker(int(sys.argv[2]))
    else:
        monitor()
