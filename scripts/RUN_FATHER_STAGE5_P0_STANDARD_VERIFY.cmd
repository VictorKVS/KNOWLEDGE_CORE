@echo off
setlocal
chcp 65001 >nul

echo ============================================================
echo FATHER - Stage 5 P0 Standard Official Verification
echo ============================================================
echo Stage4: G:\1\FATHER_LIBRARY_STAGE4
echo Output: G:\1\FATHER_LIBRARY_STAGE5
echo Mode: apply verified Rosstandart seed / no source modification
echo.

python "%~dp0father_stage5_apply_p0_standard_seed.py"
set "RC=%ERRORLEVEL%"

echo.
echo ============================================================
if "%RC%"=="0" (
  echo STAGE 5 P0 STANDARD VERIFICATION COMPLETE
) else (
  echo STAGE 5 COMPLETE WITH REVIEW ITEMS - code %RC%
)
echo Report: G:\1\FATHER_LIBRARY_STAGE5\LATEST_STAGE5_P0_STANDARD_REPORT.md
echo ============================================================
exit /b %RC%
