@echo off
setlocal
chcp 65001 >nul

echo ============================================================
echo FATHER - Stage 7 AI Regulatory Enrichment Merge
echo ============================================================
echo Stage6: G:\1\FATHER_LIBRARY_STAGE6_LEGAL
echo Output: G:\1\FATHER_LIBRARY_STAGE7
echo Mode: identity merge only / no source modification
echo.

python "%~dp0father_stage7_merge_ai_regulatory_supplement.py"
set "RC=%ERRORLEVEL%"

echo.
echo ============================================================
if "%RC%"=="0" (
  echo STAGE 7 AI REGULATORY MERGE COMPLETE
) else (
  echo STAGE 7 FAILED - code %RC%
)
echo Report: G:\1\FATHER_LIBRARY_STAGE7\LATEST_STAGE7_AI_REGULATORY_MERGE_REPORT.md
echo ============================================================
exit /b %RC%
