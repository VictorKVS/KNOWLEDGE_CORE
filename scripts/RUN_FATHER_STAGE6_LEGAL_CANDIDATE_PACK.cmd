@echo off
setlocal
chcp 65001 >nul

set "STAGE4=G:\1\FATHER_LIBRARY_STAGE4"
set "OUT=G:\1\FATHER_LIBRARY_STAGE6_LEGAL"

echo ============================================================
echo FATHER - Stage 6 LEGAL Candidate Pack
echo ============================================================
echo Stage4: %STAGE4%
echo Output: %OUT%
echo Mode: metadata extraction only / no legal status assertion
echo.

python "%~dp0father_stage6_legal_candidate_pack.py" --stage4 "%STAGE4%" --output "%OUT%"
set "RC=%ERRORLEVEL%"

echo.
echo ============================================================
if "%RC%"=="0" (
  echo STAGE 6 LEGAL CANDIDATE PACK COMPLETE
) else (
  echo STAGE 6 LEGAL CANDIDATE PACK FAILED - code %RC%
)
echo Report: %OUT%\LATEST_STAGE6_LEGAL_CANDIDATE_REPORT.md
echo ============================================================
exit /b %RC%
