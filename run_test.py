#!/usr/bin/env python3
import sys
import re

if len(sys.argv) < 2:
    print(f"Usage: {sys.argv[0]} <file-to-test>")
    sys.exit(2)

fname = sys.argv[1]
try:
    with open(fname, 'r', encoding='utf-8') as fh:
        content = fh.read()
except Exception as e:
    print(f"ERROR: could not open {fname}: {e}")
    sys.exit(2)

failed = False

def check(regex, msg, fail=True):
    global failed
    if re.search(regex, content, flags=re.M):
        print(f"FAIL: {msg}")
        if fail:
            failed = True

check(r'PAYMENT_TOKEN\s*=\s*\".+\"', 'hardcoded PAYMENT_TOKEN found')
check(r'MAIL_SERVER_KEY\s*=\s*\".+\"', 'hardcoded MAIL_SERVER_KEY found')
check(r'INTERNAL_AUTH\s*=\s*\".+\"', 'hardcoded INTERNAL_AUTH found')
check(r"SELECT .*%", 'SQL string formatting detected (possible SQL injection)')
check(r"subprocess\.Popen\(.*shell\s*=\s*True", 'subprocess.Popen with shell=True detected (command injection risk)')
check(r"app\.run\(.*debug\s*=\s*True", 'app.run(debug=True) detected (do not run web server in debug mode in production)')

if not re.search(r"os\.getenv\(|os\.environ\[", content):
    print('WARN: No environment variable lookups detected for secrets')

if failed:
    print('TEST FAILED')
    sys.exit(1)
else:
    print('TEST PASSED')
    sys.exit(0)
