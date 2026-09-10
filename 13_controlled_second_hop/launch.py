import json, os, subprocess, sys, time
from pathlib import Path

ROOT = Path('/data/zkx/zkx/review1/13_controlled_second_hop')
QUEUES = {
    0: ['05_AudioSet', '04_DCASE17_T4'],
    1: ['03_FSD50K', '02_UrbanSound8K'],
    2: ['01_ESC50', '06_TUT2017'],
}


def worker(gpu):
    env = os.environ.copy()
    env['CUDA_VISIBLE_DEVICES'] = str(gpu)
    env['PYTHONUNBUFFERED'] = '1'
    for dataset in QUEUES[gpu]:
        folder = ROOT / dataset
        folder.mkdir(parents=True, exist_ok=True)
        status = {'state': 'running', 'dataset': dataset, 'gpu': gpu,
                  'started_at': time.strftime('%F %T')}
        (folder / 'run_status.json').write_text(json.dumps(status, indent=2))
        with (folder / 'run.log').open('a') as log:
            p = subprocess.Popen([sys.executable, '-u', str(ROOT / 'run.py'), dataset],
                                 cwd=ROOT, env=env, stdout=log,
                                 stderr=subprocess.STDOUT)
            status['pid'] = p.pid
            (folder / 'run_status.json').write_text(json.dumps(status, indent=2))
            code = p.wait()
        status.update(state='completed' if code == 0 else 'failed',
                      exit_code=code, finished_at=time.strftime('%F %T'))
        (folder / 'run_status.json').write_text(json.dumps(status, indent=2))


if __name__ == '__main__':
    if len(sys.argv) == 3 and sys.argv[1] == 'worker':
        worker(int(sys.argv[2]))
    else:
        for gpu, queue in QUEUES.items():
            for dataset in queue:
                folder = ROOT / dataset
                folder.mkdir(parents=True, exist_ok=True)
                (folder / 'run_status.json').write_text(json.dumps({'state': 'queued', 'gpu': gpu}, indent=2))
            with (ROOT / f'gpu{gpu}.log').open('a') as log:
                subprocess.Popen([sys.executable, str(ROOT / 'launch.py'), 'worker', str(gpu)],
                                 stdin=subprocess.DEVNULL, stdout=log,
                                 stderr=subprocess.STDOUT, start_new_session=True)
