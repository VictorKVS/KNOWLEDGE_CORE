@echo off
setlocal
chcp 65001 >nul

set "INTAKE=G:\1\FATHER_LIBRARY_INTAKE"
set "OUT=G:\1\FATHER_LIBRARY_PROBE_V2"

echo ============================================================
echo FATHER - Library Content Probe V2
echo Precision-first legal/standard/book identification
echo ============================================================
echo Intake: %INTAKE%
echo Output: %OUT%
echo.

python "%~dp0father_library_content_probe_v2.py" --intake "%INTAKE%" --output "%OUT%" --progress-every 50
set "RC=%ERRORLEVEL%"

echo.
echo ============================================================
if "%RC%"=="0" (
  echo CONTENT PROBE V2 COMPLETE
) else (
  echo CONTENT PROBE V2 COMPLETE WITH FILE ERRORS - code %RC%
)
echo Report: %OUT%\LATEST_LIBRARY_PROBE_V2_REPORT.md
echo ============================================================
exit /b %RC%
