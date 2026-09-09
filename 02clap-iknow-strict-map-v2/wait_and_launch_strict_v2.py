import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path('/data/zkx/zkx/review1/02clap-iknow-strict-map-v2')
PRIMARY = Path('/data/zkx/zkx/review1/01clap-iknow')
LEGACY = Path('/data/zkx/zkx/review1/clap-iknow')
QUEUES = {
    0: ['05_AudioSet', '04_DCASE17_T4'],
    1: ['03_FSD50K', '02_UrbanSound8K'],
    2: ['01_ESC50', '06_TUT2017'],
}


def load_json(path):
    try:
        return json.loads(path.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def result_complete(folder):
    result = load_json(folder / 'results' / 'clap_iknow_results.json')
    return bool(result and result.get('completed'))


def synchronize_renamed_run(name):
    """Recover outputs written through paths captured before the directory rename."""
    target = PRIMARY / name
    if result_complete(target):
        return True
    source = LEGACY / name
    if not result_complete(source):
        return False
    (target / 'results').mkdir(parents=True, exist_ok=True)
    shutil.copy2(source / 'results' / 'clap_iknow_results.json',
                 target / 'results' / 'clap_iknow_results.json')
    status = {
        'dataset': name,
        'state': 'completed',
        'finished_at': time.strftime('%Y-%m-%d %H:%M:%S'),
        'note': 'result recovered after in-flight directory rename',
    }
    (target / 'run_status.json').write_text(json.dumps(status, indent=2))
    return True


def worker(gpu):
    environment = os.environ.copy()
    environment['CUDA_VISIBLE_DEVICES'] = str(gpu)
    environment['PYTHONUNBUFFERED'] = '1'
    for name in QUEUES[gpu]:
        folder = ROOT / name
        status = {'dataset': name, 'gpu': gpu, 'state': 'running',
                  'started_at': time.strftime('%Y-%m-%d %H:%M:%S')}
        with (folder / 'run.log').open('a') as log:
            process = subprocess.Popen(
                [sys.executable, '-u', str(folder / 'run_clap_iknow.py')],
                cwd=folder, env=environment, stdout=log,
                stderr=subprocess.STDOUT,
            )
            status['pid'] = process.pid
            (folder / 'run_status.json').write_text(json.dumps(status, indent=2))
            code = process.wait()
        status.update(
            state='completed' if code == 0 else 'failed', exit_code=code,
            finished_at=time.strftime('%Y-%m-%d %H:%M:%S'),
        )
        (folder / 'run_status.json').write_text(json.dumps(status, indent=2))


def monitor():
    monitor_status = ROOT / 'launch_status.json'
    launched = set()
    while len(launched) < len(QUEUES):
        completed = {
            name: synchronize_renamed_run(name)
            for queue in QUEUES.values() for name in queue
        }
        for gpu, queue in QUEUES.items():
            if gpu in launched or not all(completed[name] for name in queue):
                continue
            for name in queue:
                (ROOT / name / 'run_status.json').write_text(
                    json.dumps({'state': 'queued', 'gpu': gpu}, indent=2)
                )
            with (ROOT / f'gpu{gpu}_queue.log').open('a') as log:
                subprocess.Popen(
                    [sys.executable, str(Path(__file__).resolve()), 'worker', str(gpu)],
                    stdin=subprocess.DEVNULL, stdout=log,
                    stderr=subprocess.STDOUT, start_new_session=True,
                )
            launched.add(gpu)
        monitor_status.write_text(json.dumps({
            'state': 'partially_launched' if launched else 'waiting_for_01clap_iknow',
            'launched_gpus': sorted(launched),
            'completed': completed,
            'checked_at': time.strftime('%Y-%m-%d %H:%M:%S'),
        }, indent=2))
        if len(launched) < len(QUEUES):
            time.sleep(30)
    monitor_status.write_text(json.dumps({
        'state': 'all_gpu_queues_launched',
        'launched_gpus': sorted(launched),
        'launched_at': time.strftime('%Y-%m-%d %H:%M:%S'),
    }, indent=2))


if __name__ == '__main__':
    if len(sys.argv) == 3 and sys.argv[1] == 'worker':
        worker(int(sys.argv[2]))
    else:
        monitor()
