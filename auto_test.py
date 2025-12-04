import os
import platform
import subprocess
import datetime

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "test_run.log")


def now():
    return datetime.datetime.utcnow().isoformat() + "Z"


def run_command(cmd):
    start = now()
    # Log and print that the command is starting
    entry = f"[{start}] Running: {cmd}\n"
    print(entry, end="")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(entry)
    try:
        # Run interactively so stdout/stderr stream to the terminal
        subprocess.run(cmd, check=True)
        status = "TEST PASSED"
        rc = 0
    except subprocess.CalledProcessError as e:
        status = "TEST FAILED"
        rc = getattr(e, 'returncode', 'N/A')
        print(f"Command failed with exit code {rc}")
    end = now()
    # Append minimal result info to the logfile (stdout/stderr are streamed live)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{end}] ExitCode: {rc}\n")
        f.write(f"[{end}] {status}\n\n")
    return status == "TEST PASSED"


def main():
    system = platform.system()
    tests = []
    if system == "Windows":
        # Use python to import safely via run_test_importer
        tests = [["python", "run_test_importer.py", "input_backup.py"], ["python", "run_test_importer.py", "inputs.py"]]
    else:
        tests = [["bash", "run_test.sh", "input_backup.py"], ["bash", "run_test.sh", "inputs.py"]]

    overall = True
    for cmd in tests:
        ok = run_command(cmd)
        overall = overall and ok

    final = "TEST PASSED" if overall else "TEST FAILED"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{now()}] FINAL: {final}\n")
    return 0 if overall else 2


if __name__ == "__main__":
    raise SystemExit(main())
