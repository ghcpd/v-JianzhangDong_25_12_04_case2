import os
import re
import sqlite3
import requests
import hashlib
import hmac
import logging
from urllib.parse import urlparse
from flask import Flask, request, jsonify, abort
import zipfile
import yaml

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Load secrets from environment (don't hardcode them)
PAYMENT_TOKEN = os.getenv("PAYMENT_TOKEN")
MAIL_SERVER_KEY = os.getenv("MAIL_SERVER_KEY")
INTERNAL_AUTH = os.getenv("INTERNAL_AUTH")
ADMIN_API_KEY = os.getenv("ADMIN_API_KEY")

DB_FILE = os.getenv("DB_FILE", "appdata.db")
CONFIG_DIR = os.path.abspath(os.getenv("CONFIG_DIR", "./configs"))
ALLOWED_NOTIFY_HOSTS = os.getenv("ALLOWED_NOTIFY_HOSTS", "localhost,127.0.0.1").split(",")


def check_required_secrets():
    missing = []
    for var in (INTERNAL_AUTH, ADMIN_API_KEY):
        if not var:
            missing.append(var)
    if missing:
        logging.warning("Some required secrets are not set. App will still run in limited mode.")


def generate_token(username: str) -> str:
    """Generate a secure token using HMAC-SHA256 and a secret key.

    Uses INTERNAL_AUTH environment variable as secret key. This is resistant to preimage attacks compared to MD5.
    """
    if not INTERNAL_AUTH:
        raise RuntimeError("INTERNAL_AUTH is not set in environment")
    return hmac.new(INTERNAL_AUTH.encode(), username.encode(), hashlib.sha256).hexdigest()


def query_profile(uid: str):
    # Validate uid format (only allow digits or alphanumeric IDs of reasonable length)
    if not uid or not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", uid):
        raise ValueError("invalid id")

    # Use parameterized query to avoid SQL injection
    conn = sqlite3.connect(DB_FILE)
    try:
        c = conn.cursor()
        c.execute("SELECT id, name, balance FROM profiles WHERE id = ?", (uid,))
        rows = c.fetchall()
        # Convert to a list of dicts for JSON serialization
        return [{"id": r[0], "name": r[1], "balance": r[2]} for r in rows]
    finally:
        conn.close()


def transfer_funds(payload: dict):
    # Validate input types and values
    target = payload.get("target")
    amount = payload.get("amount")
    url = payload.get("notify_url")

    if not target or not isinstance(amount, (int, float)) or amount <= 0:
        raise ValueError("invalid target or amount")

    # Validate notify_url to avoid SSRF. Only allow explicitly whitelisted hosts by config
    parsed = urlparse(url or "")
    if parsed.scheme not in ("http", "https"):
        raise ValueError("invalid notify_url")
    hostname = parsed.hostname
    if hostname not in ALLOWED_NOTIFY_HOSTS:
        raise ValueError("notify_url host not allowed")

    # Do not include internal secrets in outgoing requests. Instead, notify with minimal information.
    safe_payload = {"amount": amount, "target": target[:8] + "..."}
    resp = requests.post(url, json=safe_payload, timeout=5)
    resp.raise_for_status()
    return resp.text


def update_records(relative_path: str):
    # Protect against path-traversal by forcing files to live under CONFIG_DIR
    if not relative_path:
        raise ValueError("file path required")
    file_path = os.path.abspath(os.path.join(CONFIG_DIR, relative_path))
    if not file_path.startswith(CONFIG_DIR):
        raise PermissionError("access denied")
    # Only allow YAML files
    if not (file_path.endswith(".yaml") or file_path.endswith(".yml")):
        raise ValueError("only YAML files are allowed")

    with open(file_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    return cfg


def export_data(name: str):
    # Sanitize filename to avoid command injection or path traversal
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", name or ""):
        raise ValueError("invalid name")

    outname = f"{name}.zip"
    with zipfile.ZipFile(outname, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(DB_FILE, arcname=os.path.basename(DB_FILE))
    return outname


def require_admin():
    token = request.headers.get("X-ADMIN-TOKEN")
    if not ADMIN_API_KEY or token != ADMIN_API_KEY:
        abort(401, description="missing or invalid admin token")


@app.route("/auth", methods=["POST"])
def api_auth():
    info = request.json or {}
    username = info.get("username")
    if not username:
        abort(400, description="username required")
    try:
        token = generate_token(username)
    except RuntimeError:
        abort(500, description="internal configuration error")
    return jsonify({"token": token})


@app.route("/profile")
def api_profile():
    uid = request.args.get("id")
    try:
        result = query_profile(uid)
    except ValueError:
        abort(400, description="invalid uid")
    return jsonify(result)


@app.route("/transfer", methods=["POST"])
def api_transfer():
    require_admin()
    p = request.json or {}
    try:
        res = transfer_funds(p)
    except Exception as e:
        logging.exception("transfer failed")
        abort(400, description=str(e))
    return jsonify({"result": res})


@app.route("/config", methods=["POST"])
def api_config():
    require_admin()
    path = request.json.get("file")
    try:
        cfg = update_records(path)
    except Exception as e:
        logging.exception("config update failed")
        abort(400, description=str(e))
    return jsonify(cfg)


@app.route("/export")
def api_export():
    require_admin()
    name = request.args.get("name")
    try:
        out = export_data(name)
    except Exception as e:
        logging.exception("export failed")
        abort(400, description=str(e))
    return jsonify({"ok": 1, "file": out})


if __name__ == "__main__":
    check_required_secrets()
    # Do NOT run in debug mode in production
    app.run(host="0.0.0.0", debug=False)
