@echo off
python run_tests.py input_backup.py vulnerable
if errorlevel 1 exit /b 1
python run_tests.py inputs.py fixed
if errorlevel 1 exit /b 1
echo ALL TESTS COMPLETED
