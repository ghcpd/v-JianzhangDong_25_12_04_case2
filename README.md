# Security audit, fixes and test harness

This repository contains an insecure example (original code) and a secured version plus automated tests and environment setup.

Files added/generated:

- `inputs.py` — ORIGINAL application (untouched). (Used as the baseline in the audit)
- `input_backup.py` — a backup copy created from `inputs.py` before any changes were made (original vulnerable file)
- `input.py` — secured, audited and remediated version of the application
- `report.json` — structured audit report describing each finding and fix
- `run_test.sh` — platform test script for Linux/macOS that checks for known insecure patterns
- `run_test.bat` — platform test script for Windows (PowerShell based)
- `auto_test.py` — runner that detects OS and runs the appropriate tests against both `input_backup.py` and `input.py`; writes output to `logs/test_run.log`
- `requirements.txt` — Python dependencies
- `setup.sh` — convenience script to create a virtualenv and install dependencies (Linux/macOS)
- `Dockerfile` — container environment which will run `auto_test.py` by default

Logs:
- `logs/test_run.log` — runtime log file created by `auto_test.py` when tests are run

How this is structured & what to expect

1. The original vulnerable code was copied to `input_backup.py` as a snapshot before any remediation.
2. The secure version `input.py` replaces insecure patterns with safer alternatives: environment-based secrets, parameterized SQL queries, no shell execution, path canonicalization for configs, SSRF protections, and admin token checks for sensitive endpoints.
3. The `report.json` enumerates the discovered issues, their severity, and shows the replacement code used.

Quick start (Linux/macOS)

1. Create a virtual environment and install requirements:

```bash
./setup.sh
```

2. Run the auto test runner which will test both the original (backup) and the secured file and write logs:

```bash
python auto_test.py
```

Quick start (Windows)

1. Create a virtual environment and install requirements (PowerShell):

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt
```

2. Run the auto test runner:

```powershell
python auto_test.py
```

Running tests directly

- Linux/macOS: `./run_test.sh input.py` or `./run_test.sh input_backup.py`
- Windows: `run_test.bat input.py` or `run_test.bat input_backup.py`

Interpreting results

- Each test script returns exit code `0` when no insecure patterns are detected and `1` when issues are found.
- `auto_test.py` will run tests for both files and decide overall success if `input_backup.py` fails (i.e., it contains issues) and `input.py` passes.
- All outputs and timestamps are stored in `logs/test_run.log`. That file will include per-test output and a final status line reading `TEST PASSED` or `TEST FAILED`.

Notes & next steps

- This remediation focuses on code-level fixes and detection of obvious insecure patterns; a real production deployment should integrate secure secret management (vault), complete authentication/authorization flows, proper TLS/secure transport, unit + integration tests against a real DB, and CI-based secret scanning.
