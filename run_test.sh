#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
export PYTHONPATH="$SCRIPT_DIR${PYTHONPATH:+:$PYTHONPATH}"
TARGET_MODULE="${TARGET_MODULE:-inputs}"
echo "Running tests for module: $TARGET_MODULE"
python -m pytest -q tests
