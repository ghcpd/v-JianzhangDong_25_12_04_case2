#!/usr/bin/env bash
set -euo pipefail

echo "Creating virtualenv and installing dependencies..."
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "Setup complete. To run tests locally: source .venv/bin/activate; python auto_test.py"
