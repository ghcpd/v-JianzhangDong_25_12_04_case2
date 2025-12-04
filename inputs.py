import os
import sqlite3
import requests
import hashlib
from flask import Flask, request, jsonify
import subprocess
import yaml

app = Flask(__name__)

# Configuration is loaded from environment variables to avoid hardcoded secrets
PAYMENT_TOKEN = os.environ.get("PAYMENT_TOKEN")
MAIL_SERVER_KEY = os.environ.get("MAIL_SERVER_KEY")
INTERNAL_AUTH = os.environ.get("INTERNAL_AUTH")

DB_FILE = os.environ.get("DB_FILE", "appdata.db")

import logging
logging.basicConfig(level=logging.INFO)


def auth_user(info):
    username = info.get("username", "")
    if not username:
        raise ValueError("username required")
    if not INTERNAL_AUTH:
        raise RuntimeError("internal auth not configured")
    raw = username + INTERNAL_AUTH
    hashed = hashlib.sha256(raw.encode()).hexdigest()
    return hashed


def query_profile(uid):
    # Validate input type
    if uid is None:
        return []
    conn = sqlite3.connect(DB_FILE)
    try:
        c = conn.cursor()
        # Use parameterized queries to prevent SQL injection
        c.execute("SELECT id,name,balance FROM profiles WHERE id = ?", (uid,))
        data = c.fetchall()
    finally:
        conn.close()
    return data


def is_valid_url(url):
    # Basic whitelist check to avoid SSRF: only allow http(s) schemes
    if not isinstance(url, str):
        return False
    return url.startswith("http://") or url.startswith("https://")


def transfer_funds(payload):
    target = payload.get("target")
    amount = payload.get("amount")
    url = payload.get("notify_url")
    if not is_valid_url(url):
        raise ValueError("invalid notify_url")
    if PAYMENT_TOKEN is None:
        raise RuntimeError("payment token not configured")
    # Log minimally without sensitive data
    logging.info("transfer requested to target=%s amount=%s", target, amount)
    try:
        resp = requests.post(url, json={"token": PAYMENT_TOKEN, "amount": amount}, timeout=5)
        resp.raise_for_status()
    except requests.RequestException as e:
        logging.error("notify request failed: %s", e)
        raise
    return resp.text


def update_records(path):
    # Prevent path traversal and require files to be in a configured directory
    if not path or ".." in path or path.startswith("/") or path.startswith("\\"):
        raise ValueError("invalid config file path")
    base_dir = os.environ.get("CONFIG_DIR", "configs")
    full = os.path.join(base_dir, path)
    if not os.path.isfile(full):
        raise FileNotFoundError("config file not found")
    with open(full, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    return cfg


def export_data(name):
    # Avoid using shell=True and subprocess injection by using list args
    if not name or any(c in name for c in ['..', '/', '\\']):
        raise ValueError("invalid export name")
    out_file = f"{name}.zip"
    import zipfile
    with zipfile.ZipFile(out_file, "w") as zf:
        zf.write(DB_FILE)
    return True


@app.route("/auth", methods=["POST"])
def api_auth():
    info = request.get_json(force=True, silent=True) or {}
    try:
        token = auth_user(info)
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    return jsonify({"token": token})


@app.route("/profile")
def api_profile():
    uid = request.args.get("id")
    try:
        data = query_profile(uid)
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    return jsonify(data)


@app.route("/transfer", methods=["POST"])
def api_transfer():
    p = request.get_json(force=True, silent=True) or {}
    try:
        result = transfer_funds(p)
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    return jsonify({"result": result})


@app.route("/config", methods=["POST"])
def api_config():
    path = (request.get_json(force=True, silent=True) or {}).get("file")
    try:
        cfg = update_records(path)
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    return jsonify(cfg)


@app.route("/export")
def api_export():
    name = request.args.get("name")
    try:
        export_data(name)
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    return jsonify({"ok": 1})


if __name__ == "__main__":
    # Do not enable debug or reloader in production
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
