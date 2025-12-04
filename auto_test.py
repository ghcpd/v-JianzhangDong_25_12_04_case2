import os
import subprocess
import sys
from datetime import datetime

LOG_DIR = os.path.join('logs')
LOG_FILE = os.path.join(LOG_DIR, 'test_run.log')
os.makedirs(LOG_DIR, exist_ok=True)

ROOT = os.path.abspath(os.path.dirname(__file__))
BACKUP = os.path.join(ROOT, 'input_backup.py')
FIXED = os.path.join(ROOT, 'input.py')

is_windows = sys.platform.startswith('win')

if is_windows:
    test_cmd = lambda target: [os.path.join(ROOT, 'run_test.bat'), target]
else:
    test_cmd = lambda target: ['bash', os.path.join(ROOT, 'run_test.sh'), target]


def run_test_and_log(target_path):
    cmd = test_cmd(target_path)
    ts = datetime.utcnow().isoformat() + 'Z'
    header = f'[{ts}] RUNNING TESTS FOR: {os.path.basename(target_path)}\n'
    with open(LOG_FILE, 'a', encoding='utf-8') as lf:
        lf.write(header)
        lf.flush()
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        out, _ = proc.communicate()
        lf.write(out + '\n')
        status = 'PASSED' if proc.returncode == 0 else 'FAILED'
        lf.write(f'[{datetime.utcnow().isoformat()}Z] {os.path.basename(target_path)} STATUS: {status} (exit {proc.returncode})\n\n')
    return proc.returncode, out


def main():
    # Run backup tests first (expected to FAIL)
    backup_rc, backup_out = run_test_and_log(BACKUP)
    # Run fixed tests (expected to PASS)
    fixed_rc, fixed_out = run_test_and_log(FIXED)

    overall_pass = (backup_rc != 0) and (fixed_rc == 0)
    final_ts = datetime.utcnow().isoformat() + 'Z'
    with open(LOG_FILE, 'a', encoding='utf-8') as lf:
        lf.write(f'[{final_ts}] FINAL STATUS: TEST PASSED\n' if overall_pass else f'[{final_ts}] FINAL STATUS: TEST FAILED\n')

    print('LOGS WRITTEN TO', LOG_FILE)
    if overall_pass:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == '__main__':
    main()
