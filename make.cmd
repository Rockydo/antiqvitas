@echo off
setlocal
set "PYTHON=python"
if exist "%~dp0.venv\Scripts\python.exe" set "PYTHON=%~dp0.venv\Scripts\python.exe"
set "TARGET=%~1"
if "%TARGET%"=="" set "TARGET=validate"
if /I "%TARGET%"=="validate" goto validate
if /I "%TARGET%"=="smoke" goto smoke
if /I "%TARGET%"=="full" goto full
echo Unknown target: %TARGET%
exit /b 2

:validate
"%PYTHON%" tools\pdxlint.py || exit /b 1
"%PYTHON%" tools\popcheck.py || exit /b 1
exit /b 0

:smoke
"%PYTHON%" tools\smoketest.py || exit /b 1
exit /b 0

:full
call "%~f0" validate || exit /b 1
call "%~f0" smoke || exit /b 1
exit /b 0
