@echo off
setlocal
cd /d "%~dp0"

set PY=C:\Users\1\AppData\Local\Programs\Python\Python312\python.exe
if not exist "%PY%" set PY=python

%PY% ".\init_father_knowledge_db.py"
set RC=%ERRORLEVEL%

echo.
echo ExitCode=%RC%
pause
exit /b %RC%
