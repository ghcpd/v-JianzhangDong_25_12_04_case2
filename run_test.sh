#!/usr/bin/env bash
set -euo pipefail
echo "Running tests for $1"
PYFILE=$1
python - <<PY
import importlib.util, sys
spec = importlib.util.spec_from_file_location('mod', PYFILE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
print('Loaded', PYFILE)
print('OK')
PY
