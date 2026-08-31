@echo off
setlocal
chcp 65001 >nul

set "ROOT=G:\1\OTUS\Библиотека"
set "OUT=G:\1\FATHER_LIBRARY_INTAKE"

echo ============================================================
echo FATHER - Library Intake Scan
echo ============================================================
echo Root: %ROOT%
echo Output: %OUT%
echo Mode: full SHA-256
echo.

python "%~dp0father_library_intake.py" --root "%ROOT%" --output "%OUT%" --mode full --progress-every 100
set "RC=%ERRORLEVEL%"

echo.
echo ============================================================
if "%RC%"=="0" (
  echo SCAN COMPLETE
) else (
  echo SCAN COMPLETE WITH FILE ERRORS - code %RC%
)
echo Report: %OUT%\LATEST_LIBRARY_INTAKE_REPORT.md
echo Registry: %OUT%\library_source_registry.csv
echo ============================================================
exit /b %RC%
