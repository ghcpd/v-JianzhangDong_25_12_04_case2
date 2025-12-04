@echo off
if "%~1"=="" (
  echo Usage: %~nx0 ^<file-to-test^>
  exit /b 2
)

set FILE=%~1
python -u run_test.py %FILE%
exit /b %ERRORLEVEL%
