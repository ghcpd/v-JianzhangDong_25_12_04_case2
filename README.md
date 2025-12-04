Overview

This workspace contains an audited and repaired Python web module and supporting test and automation artifacts.

Files generated:
- input_backup.py : Original vulnerable copy (preserved as backup)
- input.py : Hardened, secure implementation
- tests/test_vulnerabilities.py : Unit tests that detect and verify the vulnerabilities
- report.json : Structured vulnerability report with fixes and line references
- requirements.txt : Python dependencies for reproducing environment
- Dockerfile : Container specification to run the tests
- setup.sh : Script to create a python venv and install dependencies (Linux/macOS)
- run_test.sh : Runs tests (Linux/macOS) against a target file; usage: ./run_test.sh <path>
- run_test.bat : Runs tests (Windows) against a target file; usage: run_test.bat <path>
- auto_test.py : Automatic test runner that executes tests for input_backup.py and input.py and writes logs
- logs/test_run.log : Generated test run log file (created by auto_test.py)

Setup

Linux/macOS:
1. Install Python 3.11+
2. Run: bash setup.sh
3. Activate the virtualenv: source .venv/bin/activate

Windows:
1. Install Python 3.11+
2. Create virtualenv and install reqs manually:
   python -m venv .venv
   .\.venv\Scripts\activate
   pip install -r requirements.txt

Docker:
1. Build: docker build -t input-audit .
2. Run: docker run --rm input-audit

Running tests

Run tests manually for a target file:
- Linux/macOS: ./run_test.sh <path_to_target_py>
- Windows: run_test.bat <path_to_target_py>

Examples:
- ./run_test.sh input_backup.py
- ./run_test.sh input.py

Running automatic verification

Run: python auto_test.py
This will:
- Execute tests for input_backup.py (expected to FAIL)
- Execute tests for input.py (expected to PASS)
- Write detailed logs to logs/test_run.log with timestamps and final status line: TEST PASSED or TEST FAILED

Interpreting logs/test_run.log

Each test run includes a timestamp, the test output, per-file status, and a final status line. Look for the final status line to decide overall success.

Notes

- Secrets are expected to be provided via environment variables in production: PAYMENT_TOKEN, MAIL_SERVER_KEY, INTERNAL_AUTH.
- The secure code uses ALLOWED_NOTIFY_HOSTS env var to restrict notify_url hosts when performing external requests.
