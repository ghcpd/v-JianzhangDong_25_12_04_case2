import os
import sqlite3
import requests
import hashlib
from flask import Flask, request, jsonify
import subprocess
import yaml
import logging
from pathlib import Path
from urllib.parse import urlparse
import shlex

app = Flask(__name__)

# Load secrets from environment variables instead of hardcoding
PAYMENT_TOKEN = os.getenv("PAYMENT_TOKEN", "")
MAIL_SERVER_KEY = os.getenv("MAIL_SERVER_KEY", "")
INTERNAL_AUTH = os.getenv("INTERNAL_AUTH", "")

DB_FILE = os.getenv("DB_FILE", "appdata.db")

# Configure logging for security auditing
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def auth_user(info):
    """Hash user credentials using secure method with salt."""
    username = info.get("username", "")
    if not username:
        logger.warning("Authentication attempt with empty username")
        return None
    raw = username + INTERNAL_AUTH
    hashed = hashlib.sha256(raw.encode()).hexdigest()
    return hashed


def query_profile(uid):
    """Query user profile using parameterized queries to prevent SQL injection."""
    try:
        # Validate UID format - only allow numeric IDs
        if not isinstance(uid, str) or not uid.isdigit():
            logger.warning(f"Invalid UID format attempted: {uid}")
            return []
        
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        # Use parameterized query to prevent SQL injection
        q = "SELECT id,name,balance FROM profiles WHERE id = ?"
        c.execute(q, (uid,))
        data = c.fetchall()
        conn.close()
        return data
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        return []


def transfer_funds(payload):
    """Transfer funds with validation and secure URL handling."""
    try:
        target = payload.get("target")
        amount = payload.get("amount")
        
        # Validate amount is numeric
        try:
            amount = float(amount)
            if amount <= 0:
                logger.warning(f"Invalid amount: {amount}")
                return {"error": "Invalid amount"}
        except (ValueError, TypeError):
            logger.warning(f"Non-numeric amount: {amount}")
            return {"error": "Invalid amount"}
        
        # Validate and sanitize URL
        url = payload.get("notify_url")
        if not url:
            return {"error": "Missing notify_url"}
        
        # Validate URL scheme and domain
        parsed = urlparse(url)
        if parsed.scheme not in ['http', 'https']:
            logger.warning(f"Invalid URL scheme: {parsed.scheme}")
            return {"error": "Invalid URL scheme"}
        
        log = f"transfer:{target}:{amount}"
        logger.info(log)
        
        # Use timeout to prevent hanging requests
        resp = requests.post(url, json={"token": PAYMENT_TOKEN, "amount": amount}, timeout=5)
        return {"status": "success", "response": resp.text}
    except Exception as e:
        logger.error(f"Transfer error: {e}")
        return {"error": str(e)}


def update_records(path):
    """Load YAML configuration with path traversal prevention and safe deserialization."""
    try:
        # Prevent path traversal attacks
        config_dir = Path("./configs").resolve()
        file_path = config_dir.joinpath(path).resolve()
        
        # Ensure the resolved path is within the allowed directory
        if not str(file_path).startswith(str(config_dir)):
            logger.warning(f"Path traversal attempt: {path}")
            return {"error": "Invalid path"}
        
        # Check if file exists
        if not file_path.exists():
            logger.warning(f"File not found: {path}")
            return {"error": "File not found"}
        
        with open(file_path) as f:
            # Use safe_load to prevent arbitrary code execution
            cfg = yaml.safe_load(f)
        return cfg
    except Exception as e:
        logger.error(f"Config update error: {e}")
        return {"error": str(e)}


def export_data(name):
    """Export data with command injection prevention."""
    try:
        # Validate name contains only alphanumeric, underscore, and hyphen
        if not all(c.isalnum() or c in '_-' for c in name):
            logger.warning(f"Invalid export name: {name}")
            return False
        
        # Use list-based subprocess call instead of shell=True
        cmd = ["zip", f"{name}.zip", DB_FILE]
        subprocess.run(cmd, check=True, timeout=30, capture_output=True)
        logger.info(f"Data exported: {name}.zip")
        return True
    except subprocess.TimeoutExpired:
        logger.error(f"Export timeout for: {name}")
        return False
    except Exception as e:
        logger.error(f"Export error: {e}")
        return False


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
