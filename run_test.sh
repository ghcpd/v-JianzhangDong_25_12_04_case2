#!/usr/bin/env bash
set -e

if [ -z "$1" ]; then
  echo "Usage: $0 <file-to-test>" >&2
  exit 2
fi

FILE="$1"
FAIL=0

echo "Testing $FILE"

# Check for hardcoded secrets
if grep -E "PAYMENT_TOKEN\s*=\s*\".+\"" "$FILE" >/dev/null; then
  echo "FAIL: hardcoded PAYMENT_TOKEN found"
  FAIL=1
fi
if grep -E "MAIL_SERVER_KEY\s*=\s*\".+\"" "$FILE" >/dev/null; then
  echo "FAIL: hardcoded MAIL_SERVER_KEY found"
  FAIL=1
fi
if grep -E "INTERNAL_AUTH\s*=\s*\".+\"" "$FILE" >/dev/null; then
  echo "FAIL: hardcoded INTERNAL_AUTH found"
  FAIL=1
fi

# Check for unsafe SQL string formatting
if grep -E "SELECT .*%.*" "$FILE" >/dev/null || grep -E "\%\s*uid" "$FILE" >/dev/null; then
  echo "FAIL: SQL string formatting detected (possible SQL injection)"
  FAIL=1
fi

# Check for subprocess with shell=True
if grep -E "subprocess\.Popen\(.*shell\s*=\s*True" "$FILE" >/dev/null; then
  echo "FAIL: subprocess.Popen with shell=True detected (command injection risk)"
  FAIL=1
fi

# Check for debug mode
if grep -E "app\.run\(.*debug\s*=\s*True" "$FILE" >/dev/null; then
  echo "FAIL: app.run(debug=True) detected (do not run web server in debug mode in production)"
  FAIL=1
fi

# Check for environment-based secrets
if ! grep -E "os\.getenv\(|os\.environ\[" "$FILE" >/dev/null; then
  echo "WARN: No environment variable lookups detected for secrets"
fi

if [ $FAIL -eq 0 ]; then
  echo "TEST PASSED"
else
  echo "TEST FAILED"
fi

exit $FAIL
