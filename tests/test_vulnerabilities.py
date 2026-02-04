import importlib.util
import sys
from pathlib import Path

# Helper to load source as text
base = Path(__file__).resolve().parents[1]
backup_path = base / 'input_backup.py'
fixed_path = base / 'input.py'

# We'll run tests against a path specified by environment variable TARGET_FILE
import os
TARGET = os.environ.get('TARGET_FILE', str(backup_path))

source = Path(TARGET).read_text()


def test_no_hardcoded_secrets():
    # These constants must not be present as hardcoded string literals
    import re
    assert not re.search(r"PAYMENT_TOKEN\s*=\s*['\"]", source), 'PAYMENT_TOKEN is hardcoded as a string literal'
    assert not re.search(r"MAIL_SERVER_KEY\s*=\s*['\"]", source), 'MAIL_SERVER_KEY is hardcoded as a string literal'
    assert not re.search(r"INTERNAL_AUTH\s*=\s*['\"]", source), 'INTERNAL_AUTH is hardcoded as a string literal'


def test_no_sql_string_formatting():
    # SQL should not be built via string formatting with user input
    assert "% uid" not in source, 'SQL uses unsafe string formatting'
    assert "'SELECT id,name,balance FROM profiles WHERE id = '%s'" not in source


def test_no_shell_true_with_user_input():
    # export_data should not use shell=True with user-supplied name
    assert 'shell=True' not in source, 'Uses shell=True for subprocess calls'


def test_no_open_of_user_path():
    # update_records should not open a path supplied directly by user
    assert 'def update_records(path):' not in source or 'open(path)' not in source, 'Directly opening user-supplied path'


def test_no_requests_to_user_controlled_url():
    # transfer_funds must validate the notify_url before posting
    if 'requests.post(url' in source:
        assert 'ALLOWED_NOTIFY_HOSTS' in source and 'urlparse' in source, 'Posting to a user-controlled URL must be validated via ALLOWED_NOTIFY_HOSTS and urlparse'


def test_debug_disabled():
    # Debug mode is acceptable only when guarded by an explicit DEBUG env check
    if 'app.run(debug=True)' in source:
        assert "os.getenv('DEBUG'" in source or 'os.getenv("DEBUG"' in source, 'Debug mode should be enabled only under a DEBUG env flag'
