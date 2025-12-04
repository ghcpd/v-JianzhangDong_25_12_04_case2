#!/usr/bin/env bash
set -e
if [ -z "$1" ]; then
  echo "Usage: $0 <path_to_target_py>"
  exit 2
fi
TARGET_FILE="$1"
export TARGET_FILE
pytest -q tests/test_vulnerabilities.py
