import os
import sys
import platform
import subprocess
from datetime import datetime

LOG_DIR = os.path.join("logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "test_run.log")

def now():
    return datetime.utcnow().isoformat() + "Z"

def run_command(cmd):
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=False)
    return proc.returncode, proc.stdout.decode('utf-8', errors='replace')

def main():
    # Determine environment
    system = platform.system()
    if os.path.exists("/.dockerenv"):
        system = "Docker"

    if system == "Windows":
        test_cmd = ["cmd.exe", "/c", "run_test.bat"]
    else:
        test_cmd = ["/bin/bash", "run_test.sh"]

    tests = [
        ("input_backup.py", test_cmd + ["input_backup.py"]),
        ("input.py", test_cmd + ["input.py"]),
    ]

    overall_ok = True

    with open(LOG_FILE, "a", encoding="utf-8") as log:
        header = f"\n=== Test run at {now()} on {system} ===\n"
        log.write(header)
        print(header.strip())

        results = []
        for fname, cmd in tests:
            log.write(f"\n-- Running tests for {fname} at {now()} --\n")
            print(f"Running: {' '.join(cmd)}")
            code, output = run_command(cmd)
            log.write(output + "\n")
            status_line = "TEST PASSED" if code == 0 else "TEST FAILED"
            log.write(f"{now()} - {fname} - {status_line} (exit {code})\n")
            print(f"{fname}: {status_line} (exit {code})")
            results.append((fname, code, output))

        # Evaluate success conditions for verification: backup should fail and secure should pass
        backup_code = results[0][1]
        secure_code = results[1][1]

        if backup_code != 0 and secure_code == 0:
            final = "TEST PASSED"
            overall_ok = True
        else:
            final = "TEST FAILED"
            overall_ok = False

        log.write(f"\n=== Final status at {now()}: {final} ===\n")
        print(f"Final status: {final}")

    return 0 if overall_ok else 2

if __name__ == '__main__':
    sys.exit(main())
