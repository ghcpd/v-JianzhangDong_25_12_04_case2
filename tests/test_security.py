import importlib
import os
import sys
import sqlite3
import hmac
import hashlib
from pathlib import Path
from unittest import mock

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

TARGET_MODULE = os.environ.get("TARGET_MODULE", "inputs")


def reload_target(monkeypatch, env=None):
    env = env or {}
    for k, v in env.items():
        monkeypatch.setenv(k, v)
    # ensure a clean import for each test scenario
    if TARGET_MODULE in sys.modules:
        del sys.modules[TARGET_MODULE]
    return importlib.import_module(TARGET_MODULE)


@pytest.fixture
def temp_db(tmp_path):
    db_path = tmp_path / "test.db"
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("CREATE TABLE profiles (id INTEGER PRIMARY KEY, name TEXT, balance REAL)")
    c.execute("INSERT INTO profiles (id,name,balance) VALUES (1,'Alice',100.0)")
    conn.commit()
    conn.close()
    return db_path


@pytest.fixture
def config_dir(tmp_path, monkeypatch):
    cfg_dir = tmp_path / "config"
    cfg_dir.mkdir()
    valid = cfg_dir / "valid.yaml"
    valid.write_text("key: value\n")
    monkeypatch.setenv("CONFIG_DIR", str(cfg_dir))
    return cfg_dir


def test_auth_user_uses_hmac_sha256(monkeypatch):
    secret = "supersecret"
    mod = reload_target(monkeypatch, {"INTERNAL_AUTH_SECRET": secret})
    token = mod.auth_user({"username": "alice"})
    expected = hmac.new(secret.encode(), b"alice", hashlib.sha256).hexdigest()
    assert token == expected


def test_query_profile_rejects_sql_injection(monkeypatch, temp_db):
    mod = reload_target(monkeypatch, {"DB_FILE": str(temp_db)})
    with pytest.raises(ValueError):
        mod.query_profile("1 OR 1=1")


@mock.patch("requests.post")
def test_transfer_funds_blocks_insecure_urls(mock_post, monkeypatch):
    mock_resp = mock.Mock()
    mock_resp.status_code = 200
    mock_resp.text = "ok"
    mock_resp.raise_for_status.return_value = None
    mock_post.return_value = mock_resp

    env = {
        "PAYMENT_TOKEN": "tok_test",
        "ALLOWED_NOTIFY_HOSTS": "example.com",
        "INTERNAL_AUTH_SECRET": "dummy",  # may be unused here but ensures consistency
    }
    mod = reload_target(monkeypatch, env)

    # Allowed HTTPS and host
    result = mod.transfer_funds({
        "target": "bob",
        "amount": "10.5",
        "notify_url": "https://example.com/hook",
    })
    assert result == "ok"
    # ensure timeout is used to avoid hanging
    assert mock_post.call_args.kwargs.get("timeout") == 5

    # HTTP should be rejected
    with pytest.raises(ValueError):
        mod.transfer_funds({"target": "bob", "amount": 1, "notify_url": "http://example.com"})

    # Disallowed host should be rejected
    with pytest.raises(ValueError):
        mod.transfer_funds({"target": "bob", "amount": 1, "notify_url": "https://evil.com"})


def test_export_data_sanitizes_and_creates_zip(monkeypatch, tmp_path):
    # create a dummy db file
    db_file = tmp_path / "appdata.db"
    db_file.write_text("dummy")
    env = {"DB_FILE": str(db_file)}
    mod = reload_target(monkeypatch, env)

    zip_path_str = mod.export_data("bad;rm -rf /")
    zip_path = Path(zip_path_str)
    assert zip_path.exists(), "zip file should be created"
    assert "_" in zip_path.name, "unsafe characters should be sanitized"


def test_update_records_blocks_path_traversal(config_dir, monkeypatch):
    mod = reload_target(monkeypatch)
    # valid read
    cfg = mod.update_records("valid.yaml")
    assert cfg == {"key": "value"}

    # path traversal attempt should fail
    with pytest.raises(ValueError):
        mod.update_records("../inputs.py")
