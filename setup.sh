#!/usr/bin/env bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
echo "Environment set up. Activate with: source .venv/bin/activate"
