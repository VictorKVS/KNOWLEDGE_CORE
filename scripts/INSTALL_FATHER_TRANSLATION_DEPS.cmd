@echo off
setlocal
set PY=C:\Users\1\AppData\Local\Programs\Python\Python312\python.exe
if not exist "%PY%" set PY=python

%PY% -m pip install --upgrade pypdf python-docx ebooklib beautifulsoup4
set RC=%ERRORLEVEL%

echo.
echo ExitCode=%RC%
pause
exit /b %RC%
