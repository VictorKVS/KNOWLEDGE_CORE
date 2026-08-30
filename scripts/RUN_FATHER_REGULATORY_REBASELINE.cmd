@echo off
setlocal
chcp 65001 >nul

set "OUT=G:\1\FATHER_LIBRARY_REBASELINE_20260830"
set "ROOT1=G:\1\OTUS\Библиотека"
set "ROOT2=G:\1\KNOWLEDGE_CORE_IMPORT_20260827-162116\sources"

echo ============================================================
echo FATHER - Regulatory Rebaseline
echo ============================================================
echo Root 1: %ROOT1%
echo Root 2: %ROOT2%
echo Output: %OUT%
echo Mode: physical coverage only / read-only / no legal assertion
echo.

python "%~dp0father_rebaseline_regulatory_coverage.py" --root "%ROOT1%" --root "%ROOT2%" --output "%OUT%"
set "RC=%ERRORLEVEL%"

echo.
echo ============================================================
if "%RC%"=="0" (
  echo REGULATORY REBASELINE COMPLETE
) else (
  echo REGULATORY REBASELINE FAILED - code %RC%
)
echo Report: %OUT%\LATEST_REBASELINE_REPORT.md
echo ============================================================
exit /b %RC%
