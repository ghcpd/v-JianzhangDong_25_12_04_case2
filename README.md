# Security audit and test harness

Overview
- `inputs.py` : Hardened application code (secure version).
- `input_backup.py` : Original, vulnerable copy preserved for comparison.
- `report.json` : Structured vulnerability report with fixes and explanations.
- `requirements.txt` : Python dependencies.
- `Dockerfile` : Container image for running the app.
- `setup.sh` : Sets up a Python virtualenv and installs deps (Linux/macOS).
- `run_test.sh` : Runs a basic import smoke-test for a given python file (Linux/macOS).
- `run_test.bat` : Windows runner for smoke tests.
- `auto_test.py` : Detects environment and runs tests for `input_backup.py` and `inputs.py`, logs to `logs/test_run.log`.
- `logs/test_run.log` : Test output log (created by `auto_test.py`).

Setup
1. Linux/macOS
```bash
chmod +x setup.sh run_test.sh
./setup.sh
```

2. Windows
- Create a virtualenv and `pip install -r requirements.txt` manually.

Running tests
- Linux/macOS: `./run_test.sh inputs.py` or `./run_test.sh input_backup.py`
- Windows: `run_test.bat inputs.py`
- Automatic: `python auto_test.py` (will create `logs/test_run.log`)

Interpreting logs
- Each test run is logged with UTC timestamp, stdout, stderr, and a final `TEST PASSED` or `TEST FAILED` entry.
