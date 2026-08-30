@echo off
setlocal
chcp 65001 >nul

set "INTAKE=G:\1\FATHER_LIBRARY_INTAKE"
set "OUT=G:\1\FATHER_LIBRARY_PROBE"

echo ============================================================
echo FATHER - Library Content Probe (Stage 2)
echo ============================================================
echo Intake: %INTAKE%
echo Output: %OUT%
echo Mode: bounded content identification, no OCR
echo.

python -c "import pypdf" >nul 2>&1
if errorlevel 1 (
  echo ERROR: Python package pypdf is not installed.
  echo Run: python -m pip install pypdf
  exit /b 3
)

python "%~dp0father_library_content_probe.py" --intake "%INTAKE%" --output "%OUT%" --progress-every 50
set "RC=%ERRORLEVEL%"

echo.
echo ============================================================
if "%RC%"=="0" (
  echo CONTENT PROBE COMPLETE
) else (
  echo CONTENT PROBE COMPLETE WITH FILE ERRORS - code %RC%
)
echo Report: %OUT%\LATEST_LIBRARY_PROBE_REPORT.md
echo ============================================================
exit /b %RC%
