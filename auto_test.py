import os
import sys
import subprocess
from datetime import datetime

LOG_DIR = os.path.join('logs')
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, 'test_run.log')


def log(msg):
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f"[{datetime.utcnow().isoformat()}] {msg}\n")


def run_script(cmd, shell=False):
    start = datetime.utcnow()
    log(f"START {cmd}")
    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=shell, check=False, text=True)
        out = res.stdout
        code = res.returncode
    except Exception as e:
        out = str(e)
        code = 2
    end = datetime.utcnow()
    log(f"OUTPUT {out}")
    log(f"END {cmd} status={code} duration={(end-start).total_seconds()}s")
    return code, out


def detect_and_run():
    platform = sys.platform
    log(f"Detected platform: {platform}")
    is_docker = os.path.exists('/.dockerenv') or os.environ.get('IN_DOCKER') == '1'
    # Determine per-file commands
    tests = []
    # run_tests.py is platform independent; call via python
    tests.append((['python', 'run_tests.py', 'input_backup.py', 'vulnerable'], 'input_backup.py'))
    tests.append((['python', 'run_tests.py', 'inputs.py', 'fixed'], 'inputs.py'))

    overall_ok = True
    for cmd, name in tests:
        log(f"Starting test for {name}")
        code, out = run_script(cmd, shell=False)
        # Log per-file status
        if code == 0:
            log(f"{name}: TEST PASSED (exit={code})")
            print(f"{name}: TEST PASSED")
        else:
            log(f"{name}: TEST FAILED (exit={code})\nOUTPUT {out}")
            print(f"{name}: TEST FAILED")
            overall_ok = False

    if overall_ok:
        log('TEST PASSED')
        print('TEST PASSED')
        return 0
    else:
        log('TEST FAILED')
        print('TEST FAILED')
        return 1


if __name__ == '__main__':
    rc = detect_and_run()
    sys.exit(rc)
