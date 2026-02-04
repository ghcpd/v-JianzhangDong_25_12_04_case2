import os
import sqlite3
import requests
import hashlib
import hmac
import secrets
from flask import Flask, request, jsonify
import zipfile
import yaml
from urllib.parse import urlparse

app = Flask(__name__)

# Load secrets from environment variables
PAYMENT_TOKEN = os.getenv('PAYMENT_TOKEN')
MAIL_SERVER_KEY = os.getenv('MAIL_SERVER_KEY')
INTERNAL_AUTH = os.getenv('INTERNAL_AUTH')

DB_FILE = os.getenv('DB_FILE', 'appdata.db')
CONFIG_DIR = os.path.abspath(os.getenv('CONFIG_DIR', './configs'))
ALLOWED_NOTIFY_HOSTS = set(os.getenv('ALLOWED_NOTIFY_HOSTS', '').split(',')) if os.getenv('ALLOWED_NOTIFY_HOSTS') else set()


def auth_user(info):
    username = info.get('username', '')
    if not INTERNAL_AUTH:
        raise RuntimeError('Server misconfiguration: missing INTERNAL_AUTH')
    # Use HMAC-SHA256 with server secret
    digest = hmac.new(INTERNAL_AUTH.encode(), username.encode(), hashlib.sha256).hexdigest()
    return digest


def query_profile(uid):
    # Parameterized queries to prevent SQL injection
    if not isinstance(uid, (str, int)):
        raise ValueError('Invalid user id')
    conn = sqlite3.connect(DB_FILE)
    try:
        c = conn.cursor()
        c.execute("SELECT id,name,balance FROM profiles WHERE id = ?", (uid,))
        rows = c.fetchall()
        return rows
    finally:
        conn.close()


def transfer_funds(payload):
    target = payload.get('target')
    amount = payload.get('amount')
    url = payload.get('notify_url')
    # Basic validation
    if not url:
        raise ValueError('Missing notify_url')
    parsed = urlparse(url)
    if parsed.scheme not in ('https', 'http'):
        raise ValueError('Invalid URL scheme')
    hostname = parsed.hostname
    if ALLOWED_NOTIFY_HOSTS and hostname not in ALLOWED_NOTIFY_HOSTS:
        raise ValueError('Host not allowed')
    if not PAYMENT_TOKEN:
        raise RuntimeError('Server misconfiguration: missing PAYMENT_TOKEN')
    try:
        resp = requests.post(url, json={'token': PAYMENT_TOKEN, 'amount': amount}, timeout=5)
        resp.raise_for_status()
        return {'status': 'ok', 'code': resp.status_code}
    except requests.RequestException as e:
        return {'status': 'error', 'error': str(e)}


def update_records(filename):
    # Only allow filenames, and keep files inside CONFIG_DIR
    if os.path.isabs(filename):
        raise ValueError('Absolute paths are not allowed')
    safe_name = os.path.basename(filename)
    target_path = os.path.join(CONFIG_DIR, safe_name)
    if not os.path.commonpath([os.path.abspath(target_path), CONFIG_DIR]) == CONFIG_DIR:
        raise ValueError('Invalid config path')
    with open(target_path) as f:
        cfg = yaml.safe_load(f)
    return cfg


def export_data(name):
    # Sanitize filename: allow limited charset
    if not name or not isinstance(name, str):
        raise ValueError('Invalid name')
    safe_name = ''.join(c for c in name if c.isalnum() or c in ('-', '_')).strip()
    if not safe_name:
        safe_name = secrets.token_hex(8)
    zip_path = f"{safe_name}.zip"
    # Use Python's zipfile module to avoid shell injection
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.write(DB_FILE, arcname=os.path.basename(DB_FILE))
    return zip_path


@app.route('/auth', methods=['POST'])
def api_auth():
    info = request.json
    return jsonify({'token': auth_user(info)})


@app.route('/profile')
def api_profile():
    uid = request.args.get('id')
    return jsonify(query_profile(uid))


@app.route('/transfer', methods=['POST'])
def api_transfer():
    p = request.json
    return jsonify({'result': transfer_funds(p)})


@app.route('/config', methods=['POST'])
def api_config():
    path = request.json.get('file')
    return jsonify(update_records(path))


@app.route('/export')
def api_export():
    name = request.args.get('name')
    exported = export_data(name)
    return jsonify({'ok': 1, 'file': exported})


if __name__ == '__main__':
    # Default to non-debug mode; explicit DEBUG env var required to enable
    if os.getenv('DEBUG', '0') == '1':
        app.run(debug=True)
    else:
        app.run()
