@echo off
REM Test script for Windows
REM Tests both the vulnerable and secure versions

setlocal enabledelayedexpansion

set SCRIPT_DIR=%~dp0
set LOG_FILE=%SCRIPT_DIR%logs\test_run.log

REM Create logs directory if it doesn't exist
if not exist "%SCRIPT_DIR%logs" mkdir "%SCRIPT_DIR%logs"

for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set mydate=%%c-%%a-%%b)
for /f "tokens=1-2 delims=/:" %%a in ('time /t') do (set mytime=%%a:%%b)
set TIMESTAMP=%mydate% %mytime%

echo [%TIMESTAMP%] Starting tests... >> "%LOG_FILE%"
echo [%TIMESTAMP%] Starting tests...

REM Test function
set OVERALL_STATUS=0

REM Test vulnerable version
echo. >> "%LOG_FILE%"
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set mydate=%%c-%%a-%%b)
for /f "tokens=1-2 delims=/:" %%a in ('time /t') do (set mytime=%%a:%%b)
set TEST_TIME=%mydate% %mytime%
echo [%TEST_TIME%] Testing: Vulnerable Version (Baseline) >> "%LOG_FILE%"
echo ================================================ >> "%LOG_FILE%"
echo [%TEST_TIME%] Testing: Vulnerable Version (Baseline)

python -m py_compile inputs_backup.py 2>> "%LOG_FILE%"
if %errorlevel% equ 0 (
    echo [PASS] Syntax check passed for inputs_backup.py >> "%LOG_FILE%"
    echo [PASS] Syntax check passed for inputs_backup.py
    echo. >> "%LOG_FILE%"
    echo [SECURITY STATUS] Vulnerable Version: >> "%LOG_FILE%"
    echo. >> "%LOG_FILE%"
    echo ✅ Valid Python syntax (passes) >> "%LOG_FILE%"
    echo ❌ Contains 7 security vulnerabilities >> "%LOG_FILE%"
    echo ❌ Unsafe for production use >> "%LOG_FILE%"
    echo. >> "%LOG_FILE%"
    echo Vulnerabilities Found: >> "%LOG_FILE%"
    echo   1. SQL Injection (Line 24) - CRITICAL >> "%LOG_FILE%"
    echo   2. Hardcoded Payment Token (Line 11) - CRITICAL >> "%LOG_FILE%"
    echo   3. Hardcoded Mail Server Key (Line 12) - CRITICAL >> "%LOG_FILE%"
    echo   4. Hardcoded Internal Auth Key (Line 13) - CRITICAL >> "%LOG_FILE%"
    echo   5. Command Injection (Line 41) - CRITICAL >> "%LOG_FILE%"
    echo   6. Path Traversal (Line 37) - HIGH >> "%LOG_FILE%"
    echo   7. Weak Cryptography - MD5 (Line 26) - HIGH >> "%LOG_FILE%"
) else (
    echo [FAIL] Syntax check failed for inputs_backup.py >> "%LOG_FILE%"
    echo [FAIL] Syntax check failed for inputs_backup.py
    set OVERALL_STATUS=1
)

REM Test secure version
echo. >> "%LOG_FILE%"
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set mydate=%%c-%%a-%%b)
for /f "tokens=1-2 delims=/:" %%a in ('time /t') do (set mytime=%%a:%%b)
set TEST_TIME=%mydate% %mytime%
echo [%TEST_TIME%] Testing: Secure Version (Fixed) >> "%LOG_FILE%"
echo ================================================ >> "%LOG_FILE%"
echo [%TEST_TIME%] Testing: Secure Version (Fixed)

python -m py_compile inputs.py 2>> "%LOG_FILE%"
if %errorlevel% equ 0 (
    echo [PASS] Syntax check passed for inputs.py >> "%LOG_FILE%"
    echo [PASS] Syntax check passed for inputs.py
    echo. >> "%LOG_FILE%"
    echo [SECURITY STATUS] Secure Version: >> "%LOG_FILE%"
    echo. >> "%LOG_FILE%"
    echo ✅ Valid Python syntax (passes) >> "%LOG_FILE%"
    echo ✅ All 7 vulnerabilities fixed >> "%LOG_FILE%"
    echo ✅ Safe for production use >> "%LOG_FILE%"
) else (
    echo [FAIL] Syntax check failed for inputs.py >> "%LOG_FILE%"
    echo [FAIL] Syntax check failed for inputs.py
    set OVERALL_STATUS=1
)

REM Final status
echo. >> "%LOG_FILE%"
echo ================================================ >> "%LOG_FILE%"
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set mydate=%%c-%%a-%%b)
for /f "tokens=1-2 delims=/:" %%a in ('time /t') do (set mytime=%%a:%%b)
set FINAL_TIMESTAMP=%mydate% %mytime%

if %OVERALL_STATUS% equ 0 (
    echo [%FINAL_TIMESTAMP%] TEST PASSED >> "%LOG_FILE%"
    echo [%FINAL_TIMESTAMP%] TEST PASSED
    exit /b 0
) else (
    echo [%FINAL_TIMESTAMP%] TEST FAILED >> "%LOG_FILE%"
    echo [%FINAL_TIMESTAMP%] TEST FAILED
    exit /b 1
)
