@echo off
setlocal
cd /d "%~dp0"

set MODE=%~1
if "%MODE%"=="" set MODE=pilot

set PY=C:\Users\1\AppData\Local\Programs\Python\Python312\python.exe
if not exist "%PY%" set PY=python

%PY% ".\father_translation_factory.py" --mode %MODE%
set RC=%ERRORLEVEL%

echo.
echo ExitCode=%RC%
pause
exit /b %RC%
