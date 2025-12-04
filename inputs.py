import os
import sqlite3
import requests
import hashlib
import hmac
import logging
import secrets
from flask import Flask, request, jsonify, abort
import zipfile
import yaml
from urllib.parse import urlparse

app = Flask(__name__)

# Load secrets from environment; must be configured in production
PAYMENT_TOKEN = os.environ.get("PAYMENT_TOKEN")
MAIL_SERVER_KEY = os.environ.get("MAIL_SERVER_KEY")
INTERNAL_AUTH = os.environ.get("INTERNAL_AUTH")

DB_FILE = os.environ.get("DB_FILE", "appdata.db")
CONFIG_DIR = os.environ.get("CONFIG_DIR", "configs")
ALLOWED_NOTIFY_DOMAINS = [d.strip() for d in os.environ.get("ALLOWED_NOTIFY_DOMAINS", "example.com").split(",")]
API_KEY = os.environ.get("API_KEY")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def require_api_key():
    if not API_KEY:
        return True  # If no API key configured, skip check (dev)
    key = request.headers.get("X-API-KEY")
    if not key or not secrets.compare_digest(key, API_KEY):
        abort(401)
    return True


def auth_user(info):
    username = info.get("username", "")
    if not INTERNAL_AUTH:
        raise RuntimeError("Internal auth secret not configured")
    # Use HMAC-SHA256 instead of MD5 for token generation
    token = hmac.new(INTERNAL_AUTH.encode(), username.encode(), hashlib.sha256).hexdigest()
    return token


def query_profile(uid):
    # Validate uid is integer-like
    try:
        uid_int = int(uid)
    except Exception:
        raise ValueError("Invalid uid")
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    q = "SELECT id,name,balance FROM profiles WHERE id = ?"
    c.execute(q, (uid_int,))
    data = c.fetchall()
    conn.close()
    return data


def is_allowed_notify_url(url):
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ("https",):
            return False
        hostname = parsed.hostname
        return hostname in ALLOWED_NOTIFY_DOMAINS
    except Exception:
        return False


def transfer_funds(payload):
    target = payload.get("target")
    amount = payload.get("amount")
    if amount is None:
        raise ValueError("amount required")
    try:
        amount = float(amount)
    except Exception:
        raise ValueError("invalid amount")
    if amount <= 0:
        raise ValueError("amount must be positive")
    url = payload.get("notify_url")
    if not is_allowed_notify_url(url):
        raise ValueError("notify_url not allowed")
    logger.info("transfer:%s:%s", target, amount)
    resp = requests.post(url, json={"token": PAYMENT_TOKEN, "amount": amount}, timeout=5)
    resp.raise_for_status()
    return resp.text


def update_records(filename):
    # Only allow files from a configured directory to prevent path traversal
    base = os.path.abspath(CONFIG_DIR)
    target = os.path.abspath(os.path.join(base, filename))
    if not target.startswith(base):
        raise ValueError("invalid filename")
    with open(target) as f:
        cfg = yaml.safe_load(f)
    return cfg


def export_data(name):
    # Sanitize name and create a zip using Python's zipfile module
    if not name or any(c in name for c in ('..', '/', '\\')):
        raise ValueError("invalid name")
    zip_path = f"{name}.zip"
    with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        zf.write(DB_FILE)
    return True


@app.before_request
def check_api_key():
    # All incoming requests must pass API key check (if configured)
    return require_api_key()


@app.route("/auth", methods=["POST"])
def api_auth():
    info = request.json or {}
    try:
        return jsonify({"token": auth_user(info)})
    except Exception:
        abort(400)


@app.route("/profile")
def api_profile():
    uid = request.args.get("id")
    try:
        return jsonify(query_profile(uid))
    except Exception:
        abort(400)


@app.route("/transfer", methods=["POST"])
def api_transfer():
    p = request.json or {}
    try:
        return jsonify({"result": transfer_funds(p)})
    except Exception as e:
        logger.exception("transfer failed")
        abort(400)


@app.route("/config", methods=["POST"])
def api_config():
    filename = (request.json or {}).get("file")
    try:
        return jsonify(update_records(filename))
    except Exception:
        abort(400)


@app.route("/export")
def api_export():
    name = request.args.get("name")
    try:
        export_data(name)
        return jsonify({"ok": 1})
    except Exception:
        abort(400)


if __name__ == "__main__":
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(debug=debug)
