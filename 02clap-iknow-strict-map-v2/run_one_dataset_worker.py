import json
import os
import subprocess
import sys
import time
from pathlib import Path

folder = Path(sys.argv[1])
gpu = int(sys.argv[2])
script = sys.argv[3]
status_path = folder / "run_status.json"
env = os.environ.copy()
env["CUDA_VISIBLE_DEVICES"] = str(gpu)
env["PYTHONUNBUFFERED"] = "1"
status = {
    "dataset": folder.name,
    "gpu": gpu,
    "state": "running",
    "started_at": time.strftime("%Y-%m-%d %H:%M:%S"),
}
with (folder / "run.log").open("a") as log:
    process = subprocess.Popen(
        [sys.executable, "-u", str(folder / script)], cwd=folder, env=env,
        stdout=log, stderr=subprocess.STDOUT,
    )
    status["pid"] = process.pid
    status_path.write_text(json.dumps(status, indent=2))
    code = process.wait()
status.update(
    state="completed" if code == 0 else "failed", exit_code=code,
    finished_at=time.strftime("%Y-%m-%d %H:%M:%S"),
)
status_path.write_text(json.dumps(status, indent=2))
