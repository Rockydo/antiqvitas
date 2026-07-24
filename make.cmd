@echo off
setlocal
set "ROOT=%~dp0"
set "PYTHON=python"
if exist "%ROOT%.venv\Scripts\python.exe" set "PYTHON=%ROOT%.venv\Scripts\python.exe"
set "TARGET=%~1"
if "%TARGET%"=="" set "TARGET=validate"
"%PYTHON%" "%ROOT%tools\run_checks.py" "%TARGET%"
exit /b %errorlevel%
