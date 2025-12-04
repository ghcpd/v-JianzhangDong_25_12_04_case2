@echo off
REM Test script for Windows
REM This script performs basic security validation tests

echo ========================================
echo Security Audit Test Suite
echo ========================================
echo.

REM Set test environment variables
set PAYMENT_TOKEN=tok_test_123456
set MAIL_SERVER_KEY=mail_test_key_XYZ
set INTERNAL_AUTH=test_auth_secret_789
set ALLOWED_DOMAINS=api.payment-service.com,localhost

REM Create test directories
if not exist config mkdir config
if not exist logs mkdir logs

REM Create test database
echo Setting up test database...
echo CREATE TABLE IF NOT EXISTS profiles (id TEXT PRIMARY KEY, name TEXT NOT NULL, balance REAL NOT NULL); > db_setup.sql
echo INSERT OR REPLACE INTO profiles (id, name, balance) VALUES ('user123', 'Test User', 1000.00); >> db_setup.sql
echo INSERT OR REPLACE INTO profiles (id, name, balance) VALUES ('user456', 'Admin User', 5000.00); >> db_setup.sql

sqlite3 appdata.db < db_setup.sql 2>nul
del db_setup.sql

REM Create test config file
echo test: > config\test.yaml
echo   setting: "value" >> config\test.yaml
echo   enabled: true >> config\test.yaml

echo Test database created successfully.
echo.

REM Test counter
set TESTS_PASSED=0
set TESTS_FAILED=0

REM Test 1: Check if inputs.py exists
echo Running: Check inputs.py exists
if exist inputs.py (
    echo [32m✓ PASSED: Check inputs.py exists[0m
    set /a TESTS_PASSED+=1
) else (
    echo [31m✗ FAILED: Check inputs.py exists[0m
    set /a TESTS_FAILED+=1
)
echo.

REM Test 2: Check if inputs_backup.py exists
echo Running: Check inputs_backup.py exists
if exist inputs_backup.py (
    echo [32m✓ PASSED: Check inputs_backup.py exists[0m
    set /a TESTS_PASSED+=1
) else (
    echo [31m✗ FAILED: Check inputs_backup.py exists[0m
    set /a TESTS_FAILED+=1
)
echo.

REM Test 3: Verify no hardcoded secrets in inputs.py
echo Running: Verify no hardcoded secrets in inputs.py
findstr /C:"tok_production_998877" inputs.py >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [32m✓ PASSED: Verify no hardcoded secrets in inputs.py[0m
    set /a TESTS_PASSED+=1
) else (
    echo [31m✗ FAILED: Verify no hardcoded secrets in inputs.py[0m
    set /a TESTS_FAILED+=1
)
echo.

REM Test 4: Verify SQL parameterization
echo Running: Verify parameterized SQL queries
findstr /C:"execute(q, (uid,))" inputs.py >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [32m✓ PASSED: Verify parameterized SQL queries[0m
    set /a TESTS_PASSED+=1
) else (
    echo [31m✗ FAILED: Verify parameterized SQL queries[0m
    set /a TESTS_FAILED+=1
)
echo.

REM Test 5: Verify command injection protection
echo Running: Verify shell=False in subprocess
findstr /C:"shell=False" inputs.py >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [32m✓ PASSED: Verify shell=False in subprocess[0m
    set /a TESTS_PASSED+=1
) else (
    echo [31m✗ FAILED: Verify shell=False in subprocess[0m
    set /a TESTS_FAILED+=1
)
echo.

REM Test 6: Verify SSRF protection
echo Running: Verify SSRF protection exists
findstr /C:"ALLOWED_DOMAINS" inputs.py >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [32m✓ PASSED: Verify SSRF protection exists[0m
    set /a TESTS_PASSED+=1
) else (
    echo [31m✗ FAILED: Verify SSRF protection exists[0m
    set /a TESTS_FAILED+=1
)
echo.

REM Test 7: Verify path traversal protection
echo Running: Verify path traversal protection
findstr /C:"base_dir = os.path.abspath" inputs.py >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [32m✓ PASSED: Verify path traversal protection[0m
    set /a TESTS_PASSED+=1
) else (
    echo [31m✗ FAILED: Verify path traversal protection[0m
    set /a TESTS_FAILED+=1
)
echo.

REM Test 8: Verify SHA-256 instead of MD5
echo Running: Verify SHA-256 usage
findstr /C:"hashlib.sha256" inputs.py >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [32m✓ PASSED: Verify SHA-256 usage[0m
    set /a TESTS_PASSED+=1
) else (
    echo [31m✗ FAILED: Verify SHA-256 usage[0m
    set /a TESTS_FAILED+=1
)
echo.

REM Test 9: Check Python syntax
echo Running: Verify Python syntax
python -m py_compile inputs.py >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [32m✓ PASSED: Verify Python syntax[0m
    set /a TESTS_PASSED+=1
) else (
    echo [31m✗ FAILED: Verify Python syntax[0m
    set /a TESTS_FAILED+=1
)
echo.

REM Test 10: Check for required imports
echo Running: Verify security imports
findstr /C:"from urllib.parse import urlparse" inputs.py >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [32m✓ PASSED: Verify security imports[0m
    set /a TESTS_PASSED+=1
) else (
    echo [31m✗ FAILED: Verify security imports[0m
    set /a TESTS_FAILED+=1
)
echo.

echo ========================================
echo Test Summary
echo ========================================
echo Tests Passed: %TESTS_PASSED%
echo Tests Failed: %TESTS_FAILED%
echo.

REM Clean up test files
if exist appdata.db del appdata.db

if %TESTS_FAILED% EQU 0 (
    echo Status: TEST PASSED
    exit /b 0
) else (
    echo Status: TEST FAILED
    exit /b 1
)
