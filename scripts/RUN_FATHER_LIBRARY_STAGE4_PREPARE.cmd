@echo off
setlocal
chcp 65001 >nul

set "STAGE3=G:\1\FATHER_LIBRARY_STAGE3"
set "OUT=G:\1\FATHER_LIBRARY_STAGE4"

echo ============================================================
echo FATHER - Library Stage 4 Preparation
echo ============================================================
echo Stage3: %STAGE3%
echo Output: %OUT%
echo Mode: build verification manifests only
echo.

python "%~dp0father_library_stage4_prepare.py" --stage3 "%STAGE3%" --output "%OUT%"
set "RC=%ERRORLEVEL%"

echo.
echo ============================================================
if "%RC%"=="0" (
  echo STAGE 4 PREPARATION COMPLETE
) else (
  echo STAGE 4 PREPARATION FAILED - code %RC%
)
echo Report: %OUT%\LATEST_STAGE4_PREPARE_REPORT.md
echo ============================================================
exit /b %RC%