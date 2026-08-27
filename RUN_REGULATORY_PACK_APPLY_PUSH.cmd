@echo off
setlocal
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File ".\scripts\collect-local-regulatory-pack.ps1" -Apply -Push
set RC=%ERRORLEVEL%
echo.
echo ExitCode=%RC%
pause
exit /b %RC%
