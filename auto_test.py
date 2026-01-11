import os
import sys
import subprocess
import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LOG_DIR = ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "test_run.log"

MODULES = [
    ("input_backup", "input_backup.py"),
    ("inputs", "inputs.py"),
]


def timestamp():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def log(msg: str):
    line = f"{timestamp()} {msg}\n"
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(line)
    # also echo to stdout for visibility
    sys.stdout.write(line)
    sys.stdout.flush()


def detect_env():
    if os.path.exists("/.dockerenv") or os.environ.get("DOCKER_ENV"):
        return "docker"
    if sys.platform.startswith("win"):
        return "windows"
    return "linux"


def run_tests_for_module(module_name: str, env_type: str) -> int:
    env = os.environ.copy()
    env["TARGET_MODULE"] = module_name

    if env_type == "windows":
        cmd = ["run_test.bat"]
        shell = True
    else:
        cmd = ["bash", "run_test.sh"]
        shell = False

    log(f"=== RUN {module_name} ===")
    proc = subprocess.run(
        cmd,
        cwd=str(ROOT),
        env=env,
        capture_output=True,
        text=True,
        shell=shell,
    )
    if proc.stdout:
        log(proc.stdout.rstrip())
    if proc.stderr:
        log(proc.stderr.rstrip())
    status_line = "TEST PASSED" if proc.returncode == 0 else "TEST FAILED"
    log(status_line)
    return proc.returncode


def main():
    env_type = detect_env()
    log(f"Detected environment: {env_type}")

    results = {}
    for module_name, _ in MODULES:
        rc = run_tests_for_module(module_name, env_type)
        results[module_name] = rc

    # Overall pass if the secured module passes
    overall_pass = results.get("inputs", 1) == 0
    if overall_pass:
        log("OVERALL: TEST PASSED")
        sys.exit(0)
    else:
        log("OVERALL: TEST FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()
