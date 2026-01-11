@echo off
setlocal enabledelayedexpansion
set SCRIPT_DIR=%~dp0
pushd %SCRIPT_DIR%
if "%TARGET_MODULE%"=="" set TARGET_MODULE=inputs
echo Running tests for module: %TARGET_MODULE%
python -m pytest -q tests
set EXITCODE=%ERRORLEVEL%
popd
exit /b %EXITCODE%
