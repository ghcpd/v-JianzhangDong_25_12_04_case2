#!/bin/bash

# Test script for Linux/macOS
# This script performs basic security validation tests

echo "========================================"
echo "Security Audit Test Suite"
echo "========================================"
echo ""

# Set test environment variables
export PAYMENT_TOKEN="tok_test_123456"
export MAIL_SERVER_KEY="mail_test_key_XYZ"
export INTERNAL_AUTH="test_auth_secret_789"
export ALLOWED_DOMAINS="api.payment-service.com,localhost"

# Create test directories
mkdir -p config logs

# Create test database
echo "Setting up test database..."
sqlite3 appdata.db << EOF
CREATE TABLE IF NOT EXISTS profiles (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    balance REAL NOT NULL
);
INSERT OR REPLACE INTO profiles (id, name, balance) VALUES ('user123', 'Test User', 1000.00);
INSERT OR REPLACE INTO profiles (id, name, balance) VALUES ('user456', 'Admin User', 5000.00);
EOF

# Create test config file
cat > config/test.yaml << EOF
test:
  setting: "value"
  enabled: true
EOF

echo "Test database created successfully."
echo ""

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Function to run a test
run_test() {
    local test_name="$1"
    local test_command="$2"
    
    echo "Running: $test_name"
    if eval "$test_command"; then
        echo "✓ PASSED: $test_name"
        ((TESTS_PASSED++))
    else
        echo "✗ FAILED: $test_name"
        ((TESTS_FAILED++))
    fi
    echo ""
}

# Test 1: Check if inputs.py exists
run_test "Check inputs.py exists" "test -f inputs.py"

# Test 2: Check if inputs_backup.py exists
run_test "Check inputs_backup.py exists" "test -f inputs_backup.py"

# Test 3: Verify no hardcoded secrets in inputs.py
run_test "Verify no hardcoded secrets in inputs.py" "! grep -q 'tok_production_998877' inputs.py"

# Test 4: Verify SQL parameterization (no string formatting in SQL)
run_test "Verify parameterized SQL queries" "grep -q 'execute(q, (uid,))' inputs.py"

# Test 5: Verify command injection protection (shell=False)
run_test "Verify shell=False in subprocess" "grep -q 'shell=False' inputs.py"

# Test 6: Verify SSRF protection (URL validation)
run_test "Verify SSRF protection exists" "grep -q 'ALLOWED_DOMAINS' inputs.py"

# Test 7: Verify path traversal protection
run_test "Verify path traversal protection" "grep -q 'base_dir = os.path.abspath' inputs.py"

# Test 8: Verify SHA-256 instead of MD5
run_test "Verify SHA-256 usage" "grep -q 'hashlib.sha256' inputs.py"

# Test 9: Check Python syntax
run_test "Verify Python syntax" "python3 -m py_compile inputs.py"

# Test 10: Check for required imports
run_test "Verify security imports" "grep -q 'from urllib.parse import urlparse' inputs.py"

echo "========================================"
echo "Test Summary"
echo "========================================"
echo "Tests Passed: $TESTS_PASSED"
echo "Tests Failed: $TESTS_FAILED"
echo ""

# Clean up test files
rm -f appdata.db

if [ $TESTS_FAILED -eq 0 ]; then
    echo "Status: TEST PASSED"
    exit 0
else
    echo "Status: TEST FAILED"
    exit 1
fi
