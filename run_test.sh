#!/usr/bin/env bash
set -e
python run_tests.py input_backup.py vulnerable
python run_tests.py inputs.py fixed
echo "ALL TESTS COMPLETED"
