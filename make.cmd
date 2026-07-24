@echo off
setlocal
set "PYTHON=python"
if exist "%~dp0.venv\Scripts\python.exe" set "PYTHON=%~dp0.venv\Scripts\python.exe"
set "TARGET=%~1"
if "%TARGET%"=="" set "TARGET=validate"
"%PYTHON%" tools\run_checks.py "%TARGET%"
exit /b %errorlevel%
