@echo off
setlocal
cd /d "%~dp0"
set "INV=C:\Users\1\Documents\Codex\2026-08-26\new-chat\outputs\library_inventory.csv"
echo Inventory: %INV%
if not exist "%INV%" (
  echo ERROR: inventory CSV not found.
  echo %INV%
  pause
  exit /b 2
)
powershell.exe -NoProfile -ExecutionPolicy Bypass -File ".\scripts\collect-local-regulatory-pack.ps1" -InventoryCsv "%INV%"
set RC=%ERRORLEVEL%
echo.
echo ExitCode=%RC%
pause
exit /b %RC%
