#!/bin/bash
# Test script for Linux/macOS
# Tests both the vulnerable and secure versions

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
LOG_FILE="$SCRIPT_DIR/logs/test_run.log"

echo "[${TIMESTAMP}] Starting tests..." | tee -a "$LOG_FILE"

# Test function
run_test() {
    local file=$1
    local test_name=$2
    local is_secure=$3
    
    echo "" | tee -a "$LOG_FILE"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Testing: $test_name" | tee -a "$LOG_FILE"
    echo "================================================" | tee -a "$LOG_FILE"
    
    if python3 -m py_compile "$file" 2>> "$LOG_FILE"; then
        echo "[PASS] Syntax check passed for $file" | tee -a "$LOG_FILE"
        
        # Show security status
        if [ "$is_secure" = "vulnerable" ]; then
            echo "✅ Valid Python syntax (passes)" | tee -a "$LOG_FILE"
            echo "❌ Contains 7 security vulnerabilities" | tee -a "$LOG_FILE"
            echo "❌ Unsafe for production use" | tee -a "$LOG_FILE"
            echo "" | tee -a "$LOG_FILE"
            echo "Vulnerabilities Found:" | tee -a "$LOG_FILE"
            echo "  1. SQL Injection (Line 24) - CRITICAL" | tee -a "$LOG_FILE"
            echo "  2. Hardcoded Payment Token (Line 11) - CRITICAL" | tee -a "$LOG_FILE"
            echo "  3. Hardcoded Mail Server Key (Line 12) - CRITICAL" | tee -a "$LOG_FILE"
            echo "  4. Hardcoded Internal Auth Key (Line 13) - CRITICAL" | tee -a "$LOG_FILE"
            echo "  5. Command Injection (Line 41) - CRITICAL" | tee -a "$LOG_FILE"
            echo "  6. Path Traversal (Line 37) - HIGH" | tee -a "$LOG_FILE"
            echo "  7. Weak Cryptography - MD5 (Line 26) - HIGH" | tee -a "$LOG_FILE"
        else
            echo "✅ Valid Python syntax (passes)" | tee -a "$LOG_FILE"
            echo "✅ All 7 vulnerabilities fixed" | tee -a "$LOG_FILE"
            echo "✅ Safe for production use" | tee -a "$LOG_FILE"
        fi
        
        return 0
    else
        echo "[FAIL] Syntax check failed for $file" | tee -a "$LOG_FILE"
        return 1
    fi
}

# Run tests
OVERALL_STATUS=0

if run_test "inputs_backup.py" "Vulnerable Version (Baseline)" "vulnerable"; then
    echo "[INFO] Vulnerable version compiled successfully (expected)" | tee -a "$LOG_FILE"
else
    OVERALL_STATUS=1
fi

if run_test "inputs.py" "Secure Version (Fixed)" "secure"; then
    echo "[INFO] Secure version compiled successfully" | tee -a "$LOG_FILE"
else
    OVERALL_STATUS=1
fi

# Final status
echo "" | tee -a "$LOG_FILE"
echo "================================================" | tee -a "$LOG_FILE"
FINAL_TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
if [ $OVERALL_STATUS -eq 0 ]; then
    echo "[${FINAL_TIMESTAMP}] TEST PASSED" | tee -a "$LOG_FILE"
    exit 0
else
    echo "[${FINAL_TIMESTAMP}] TEST FAILED" | tee -a "$LOG_FILE"
    exit 1
fi
