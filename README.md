# Secure Audit of `inputs.py`

## 📂 Generated Files

| File | Purpose |
| ---- | ------- |
| `inputs.py` | **Secured** Flask app with hardened authentication, database, and file handling. |
| `input_backup.py` | Backup of the original vulnerable source (as requested). |
| `inputs_backup.py` | Convenience backup for module-based testing. |
| `report.json` | Structured vulnerability report with fixes. |
| `requirements.txt` | Python dependencies. |
| `setup.sh` | Linux/macOS setup script (creates venv, installs deps). |
| `Dockerfile` | Containerized environment for the app and tests. |
| `run_test.sh` | Linux/macOS test runner (uses `pytest`). |
| `run_test.bat` | Windows test runner. |
| `auto_test.py` | Runs tests for backup and fixed modules; logs to `logs/test_run.log`. |
| `logs/test_run.log` | Test execution logs with timestamps and pass/fail status. |

## 🛠️ Setup (Linux/macOS)

```bash
./setup.sh
```

> This creates `.venv`, upgrades `pip`, and installs dependencies from `requirements.txt`.

## 🪟 Setup (Windows)

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

## 🧪 Running Tests Manually

### Linux/macOS
```bash
# Default tests against secured module `inputs`
./run_test.sh

# Target a specific module
TARGET_MODULE=inputs ./run_test.sh
TARGET_MODULE=input_backup ./run_test.sh
```

### Windows
```powershell
# Default tests against secured module `inputs`
run_test.bat

# Target a specific module
set TARGET_MODULE=inputs
run_test.bat

set TARGET_MODULE=input_backup
run_test.bat
```

## 🤖 Automatic Test Runner (`auto_test.py`)

`auto_test.py` detects the environment (Windows/Linux/Docker) and runs:
1. Tests for `input_backup` (expected to **fail**, demonstrating vulnerabilities).
2. Tests for `inputs` (expected to **pass**, confirming fixes).

Logs are written to `logs/test_run.log` with timestamps and a final status line (`TEST PASSED` or `TEST FAILED`).

```powershell
python auto_test.py
```

## 📜 Logs

- Location: `logs/test_run.log`
- Contains: Timestamped test output for each module, plus per-run and overall status lines.
- Interpretation: Look for `TEST PASSED` / `TEST FAILED` lines. Overall success is reported as `OVERALL: TEST PASSED`.

## 🔐 Environment Variables

Set these to configure the secured app (`inputs.py`):

- `DB_FILE` – Path to SQLite database (default: `appdata.db`).
- `PAYMENT_TOKEN` – **Required** token for outbound payment notifications.
- `MAIL_SERVER_KEY` – Mail server key (placeholder, unused in this sample).
- `INTERNAL_AUTH_SECRET` – **Required** secret for HMAC-based auth tokens.
- `ALLOWED_NOTIFY_HOSTS` – Comma-separated allowed hosts for `notify_url` (e.g., `example.com`).
- `CONFIG_DIR` – Directory containing YAML configs (default: `./config`).
- `FLASK_DEBUG`, `FLASK_HOST`, `FLASK_PORT` – Flask server settings (debug defaults to off).

## 🚨 Notes

- `input_backup.py` and `inputs_backup.py` are intentionally vulnerable and should **never** be used in production.
- The tests in `tests/test_security.py` are designed to **fail** for the backup module and **pass** for the secured module.
