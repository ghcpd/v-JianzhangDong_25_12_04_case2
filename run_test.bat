@echo off
if "%1"=="" (
  echo Usage: %0 ^<path_to_target_py^>
  exit /b 2
)
set TARGET_FILE=%~1
set TARGET_FILE=%TARGET_FILE%
pytest -q tests/test_vulnerabilities.py
if %ERRORLEVEL% NEQ 0 (
  exit /b %ERRORLEVEL%
)
exit /b 0
