@echo off
if "%1"=="" (
  echo Usage: run_test.bat script.py
  exit /b 1
)
python run_test_importer.py %1
if %ERRORLEVEL% NEQ 0 (
  echo TEST FAILED
  exit /b %ERRORLEVEL%
)
echo TEST PASSED
