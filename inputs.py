import os
import sqlite3
import requests
import hashlib
import hmac
import logging
import re
from decimal import Decimal, InvalidOperation
from flask import Flask, request, jsonify
from urllib.parse import urlparse
from zipfile import ZipFile
from pathlib import Path
import yaml

app = Flask(__name__)

# Configuration
DB_FILE = os.environ.get("DB_FILE", "appdata.db")
PAYMENT_TOKEN = os.environ.get("PAYMENT_TOKEN")
MAIL_SERVER_KEY = os.environ.get("MAIL_SERVER_KEY")
INTERNAL_AUTH_SECRET = os.environ.get("INTERNAL_AUTH_SECRET")
ALLOWED_NOTIFY_HOSTS = {
    h.strip().lower()
    for h in os.environ.get("ALLOWED_NOTIFY_HOSTS", "").split(",")
    if h.strip()
}
CONFIG_DIR = os.environ.get("CONFIG_DIR", os.path.join(os.getcwd(), "config"))

# Logging
logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger(__name__)


def _require_secret(value: str, name: str) -> str:
    if not value:
        raise RuntimeError(f"Required secret {name} is not configured")
    return value


def auth_user(info):
    """Authenticate user by returning an HMAC-based token.

    This replaces the insecure MD5 hash of username + hardcoded salt.
    """
    username = (info or {}).get("username", "")
    secret = _require_secret(INTERNAL_AUTH_SECRET, "INTERNAL_AUTH_SECRET")
    token = hmac.new(secret.encode(), username.encode(), hashlib.sha256).hexdigest()
    return token


def query_profile(uid):
    """Retrieve a profile safely using a parameterized query."""
    if uid is None:
        raise ValueError("id is required")
    uid_str = str(uid)
    if not uid_str.isdigit():
        raise ValueError("id must be numeric")
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("SELECT id,name,balance FROM profiles WHERE id = ?", (int(uid_str),))
        data = c.fetchall()
    return data


def _validate_amount(amount):
    try:
        amt = Decimal(str(amount))
    except (InvalidOperation, TypeError):
        raise ValueError("amount must be a number") from None
    if amt <= 0:
        raise ValueError("amount must be positive")
    return amt


def _validate_notify_url(url: str) -> str:
    if not url:
        raise ValueError("notify_url is required")
    parsed = urlparse(url)
    if parsed.scheme != "https":
        raise ValueError("notify_url must use https")
    host = (parsed.hostname or "").lower()
    if ALLOWED_NOTIFY_HOSTS and host not in ALLOWED_NOTIFY_HOSTS:
        raise ValueError("notify_url host not allowed")
    return url


def transfer_funds(payload):
    """Transfer funds; notify only approved HTTPS endpoints and avoid SSRF."""
    payload = payload or {}
    target = payload.get("target")
    amount = _validate_amount(payload.get("amount"))
    url = _validate_notify_url(payload.get("notify_url"))

    _require_secret(PAYMENT_TOKEN, "PAYMENT_TOKEN")

    logger.info("transfer:init target=%s amount=%s", target, amount)
    resp = requests.post(url, json={"token": PAYMENT_TOKEN, "amount": str(amount)}, timeout=5)
    resp.raise_for_status()
    logger.info("transfer:success target=%s amount=%s", target, amount)
    return resp.text


def _ensure_safe_config_path(path: str) -> Path:
    if not path:
        raise ValueError("config file path is required")
    base = Path(CONFIG_DIR).resolve()
    raw_path = Path(path)
    candidate = (base / raw_path).resolve() if not raw_path.is_absolute() else raw_path.resolve()
    if not str(candidate).startswith(str(base)):
        raise ValueError("config path is not allowed")
    if candidate.suffix not in {".yml", ".yaml"}:
        raise ValueError("config file must be .yml or .yaml")
    if not candidate.exists():
        raise FileNotFoundError(f"config file not found: {candidate}")
    return candidate


def update_records(path):
    safe_path = _ensure_safe_config_path(path)
    with open(safe_path, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    return cfg


_SAFE_NAME_RE = re.compile(r"[^A-Za-z0-9_.-]")


def export_data(name):
    """Export DB file into a zip archive securely without shell commands."""
    if not name:
        raise ValueError("name is required")
    safe_name = _SAFE_NAME_RE.sub("_", str(name))
    zip_path = Path(f"{safe_name}.zip").resolve()
    with ZipFile(zip_path, "w") as zf:
        zf.write(DB_FILE, arcname=Path(DB_FILE).name)
    logger.info("exported data to %s", zip_path)
    return str(zip_path)


@app.route("/auth", methods=["POST"])
def api_auth():
    info = request.json
    return jsonify({"token": auth_user(info)})


@app.route("/profile")
def api_profile():
    uid = request.args.get("id")
    return jsonify(query_profile(uid))


@app.route("/transfer", methods=["POST"])
def api_transfer():
    p = request.json
    return jsonify({"result": transfer_funds(p)})


@app.route("/config", methods=["POST"])
def api_config():
    path = request.json.get("file")
    return jsonify(update_records(path))


@app.route("/export")
def api_export():
    name = request.args.get("name")
    zip_path = export_data(name)
    return jsonify({"ok": 1, "path": zip_path})


def _strtobool(val: str) -> bool:
    return str(val).lower() in {"1", "true", "yes", "on"}


if __name__ == "__main__":
    debug = _strtobool(os.environ.get("FLASK_DEBUG", "0"))
    host = os.environ.get("FLASK_HOST", "127.0.0.1")
    port = int(os.environ.get("FLASK_PORT", "5000"))
    app.run(debug=debug, host=host, port=port)
