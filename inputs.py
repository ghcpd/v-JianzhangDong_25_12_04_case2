import os
import sqlite3
import requests
import hashlib
from flask import Flask, request, jsonify
import subprocess
import yaml
import re
from urllib.parse import urlparse

app = Flask(__name__)

# Load secrets from environment variables instead of hardcoding
PAYMENT_TOKEN = os.environ.get("PAYMENT_TOKEN", "")
MAIL_SERVER_KEY = os.environ.get("MAIL_SERVER_KEY", "")
INTERNAL_AUTH = os.environ.get("INTERNAL_AUTH", "")

DB_FILE = "appdata.db"

# Whitelist for allowed domains in SSRF protection
ALLOWED_DOMAINS = os.environ.get("ALLOWED_DOMAINS", "api.payment-service.com").split(",")


def auth_user(info):
    # Use SHA-256 instead of MD5 for secure hashing
    raw = info.get("username", "") + INTERNAL_AUTH
    hashed = hashlib.sha256(raw.encode()).hexdigest()
    return hashed


def query_profile(uid):
    # Use parameterized queries to prevent SQL injection
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    q = "SELECT id,name,balance FROM profiles WHERE id = ?"
    c.execute(q, (uid,))
    data = c.fetchall()
    conn.close()
    return data


def transfer_funds(payload):
    target = payload.get("target")
    amount = payload.get("amount")
    log = f"transfer:{target}:{amount}"
    print(log)
    url = payload.get("notify_url")
    
    # SSRF protection: validate URL against whitelist
    try:
        parsed = urlparse(url)
        if parsed.hostname not in ALLOWED_DOMAINS:
            return "Error: URL not in allowed domains"
    except Exception as e:
        return f"Error: Invalid URL - {str(e)}"
    
    resp = requests.post(url, json={"token": PAYMENT_TOKEN, "amount": amount}, timeout=5)
    return resp.text


def update_records(path):
    # Path traversal protection: validate and sanitize path
    # Only allow files from a specific directory
    base_dir = os.path.abspath("config")
    requested_path = os.path.abspath(path)
    
    if not requested_path.startswith(base_dir):
        raise ValueError("Access denied: Path traversal detected")
    
    if not os.path.exists(requested_path):
        raise FileNotFoundError("Configuration file not found")
    
    with open(requested_path) as f:
        cfg = yaml.safe_load(f)
    return cfg


def export_data(name):
    # Command injection protection: validate input and use list form
    # Only allow alphanumeric characters and underscores
    if not re.match(r'^[a-zA-Z0-9_]+$', name):
        raise ValueError("Invalid export name: only alphanumeric characters and underscores allowed")
    
    # Use list form instead of shell=True to prevent command injection
    cmd = ["zip", f"{name}.zip", DB_FILE]
    subprocess.Popen(cmd, shell=False)
    return True


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
    export_data(name)
    return jsonify({"ok": 1})


if __name__ == "__main__":
    app.run(debug=True)
