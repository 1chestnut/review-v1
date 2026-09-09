import json, os, subprocess, sys, time
from pathlib import Path

ROOT = Path('/data/zkx/zkx/review1/07_second-hop-mp-audit')
QUEUES = {
    0: ['05_AudioSet', '04_DCASE17_T4'],
    1: ['03_FSD50K', '02_UrbanSound8K'],
    2: ['01_ESC50', '06_TUT2017'],
}

def worker(gpu):
    env = os.environ.copy()
    env['CUDA_VISIBLE_DEVICES'] = str(gpu)
    env['PYTHONUNBUFFERED'] = '1'
    for name in QUEUES[gpu]:
        folder = ROOT / name
        status = {'dataset': name, 'gpu': gpu, 'state': 'running', 'started_at': time.strftime('%F %T')}
        with (folder / 'run.log').open('a') as log:
            process = subprocess.Popen(
                [sys.executable, '-u', str(folder / 'run_mp_audit.py')],
                cwd=folder, env=env, stdout=log, stderr=subprocess.STDOUT,
            )
            status['pid'] = process.pid
            (folder / 'run_status.json').write_text(json.dumps(status, indent=2))
            code = process.wait()
        status.update(state='completed' if code == 0 else 'failed', exit_code=code,
                      finished_at=time.strftime('%F %T'))
        (folder / 'run_status.json').write_text(json.dumps(status, indent=2))

def launch():
    for gpu, queue in QUEUES.items():
        for name in queue:
            (ROOT / name / 'run_status.json').write_text(json.dumps({'state': 'queued', 'gpu': gpu}, indent=2))
        with (ROOT / f'gpu{gpu}_queue.log').open('a') as log:
            subprocess.Popen([sys.executable, str(Path(__file__).resolve()), 'worker', str(gpu)],
                             stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT,
                             start_new_session=True)
    (ROOT / 'launch_status.json').write_text(json.dumps({
        'state': 'all_gpu_queues_launched', 'launched_at': time.strftime('%F %T'),
        'queues': QUEUES,
    }, indent=2))

if __name__ == '__main__':
    worker(int(sys.argv[2])) if len(sys.argv) == 3 else launch()
