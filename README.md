# inputs.py Security Audit and Remediation

Overview
- input_backup.py: original insecure source
- inputs.py: hardened secure implementation
- report.json: structured vulnerability report
- run_tests.py: simple pattern-based tests
- run_test.sh / run_test.bat: platform test runners
- auto_test.py: automatic environment detection and test execution; logs to logs/test_run.log
- requirements.txt, Dockerfile, setup.sh: environment replication

Setup
1. Create a Python virtual environment and install deps:
   - Linux/macOS: sh setup.sh
   - Windows (PowerShell): python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt

Running tests
- Linux/macOS: ./run_test.sh
- Windows: run_test.bat
- Automatic detection and run: python auto_test.py

Check logs
- Logs are written to `logs/test_run.log` and include timestamps and final status lines TEST PASSED or TEST FAILED.

Notes
- Configure environment variables before running the app in production: PAYMENT_TOKEN, MAIL_SERVER_KEY, INTERNAL_AUTH, DB_FILE, CONFIG_DIR, ALLOWED_NOTIFY_DOMAINS, API_KEY.
- The hardened version enforces API key checks (if configured), safe SQL parameterization, HMAC-SHA256 auth token, URL whitelist for notifications, avoidance of shell commands, and more robust error handling.
