@echo off
setlocal
chcp 65001 >nul

set "PROBE=G:\1\FATHER_LIBRARY_PROBE_V2"
set "OUT=G:\1\FATHER_LIBRARY_STAGE3"

echo ============================================================
echo FATHER - Library Stage 3 Router
echo ============================================================
echo Probe: %PROBE%
echo Output: %OUT%
echo Mode: route-only / no source modification
echo.

python "%~dp0father_library_stage3_router.py" --probe "%PROBE%" --output "%OUT%"
set "RC=%ERRORLEVEL%"

echo.
echo ============================================================
if "%RC%"=="0" (
  echo STAGE 3 ROUTING COMPLETE
) else (
  echo STAGE 3 ROUTING FAILED - code %RC%
)
echo Report: %OUT%\LATEST_STAGE3_ROUTER_REPORT.md
echo ============================================================
exit /b %RC%
