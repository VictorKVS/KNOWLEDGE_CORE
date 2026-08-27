@echo off
setlocal
cd /d "%~dp0"

C:\Users\1\AppData\Local\Programs\Python\Python312\python.exe ".\regulatory_import_v5_stage_safe.py"
set RC=%ERRORLEVEL%

echo.
echo ExitCode=%RC%
pause
exit /b %RC%
