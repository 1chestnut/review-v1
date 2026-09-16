"""Copy committed manuscript files to the existing review-v1 Git repository.

Run interactively. Password is prompted and never stored in this directory.
"""

from getpass import getpass
from pathlib import Path
import subprocess
import paramiko

ROOT = Path(__file__).resolve().parent
HOST = "10.132.219.47"
USER = "star"
REMOTE_REPO = "/data/zkx/zkx/review1"
REMOTE_SUBDIR = "writing/2026-09-16"


def run_remote(ssh, command):
    _, stdout, stderr = ssh.exec_command(command)
    code = stdout.channel.recv_exit_status()
    output = stdout.read().decode(errors="replace")
    error = stderr.read().decode(errors="replace")
    if code:
        raise RuntimeError(f"Remote command failed ({code}): {command}\n{output}\n{error}")
    return output.strip()


def main():
    files = subprocess.check_output(
        ["git", "ls-files", "-z"], cwd=ROOT
    ).decode().split("\0")
    files = [name for name in files if name]
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.connect(HOST, username=USER, password=getpass(f"Password for {USER}@{HOST}: "))
    try:
        origin = run_remote(ssh, f"git -C {REMOTE_REPO} remote get-url origin")
        if "1chestnut/review-v1" not in origin:
            raise RuntimeError(f"Unexpected Git remote: {origin}")
        sftp = ssh.open_sftp()
        for relative in files:
            destination = f"{REMOTE_REPO}/{REMOTE_SUBDIR}/{relative}"
            parent = destination.rsplit("/", 1)[0]
            run_remote(ssh, f"mkdir -p '{parent}'")
            sftp.put(str(ROOT / relative), destination)
        sftp.close()
        run_remote(ssh, f"git -C {REMOTE_REPO} add -- '{REMOTE_SUBDIR}'")
        status = run_remote(ssh, f"git -C {REMOTE_REPO} status --short -- '{REMOTE_SUBDIR}'")
        print(status or "No changes to commit")
        if status:
            run_remote(
                ssh,
                f"git -C {REMOTE_REPO} commit -m 'Add Elsevier manuscript workspace' -- '{REMOTE_SUBDIR}'",
            )
            run_remote(ssh, f"git -C {REMOTE_REPO} push origin HEAD:main")
            print("Pushed to 1chestnut/review-v1, writing/2026-09-16")
    finally:
        ssh.close()


if __name__ == "__main__":
    main()
