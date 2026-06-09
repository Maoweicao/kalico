@echo off
:: Kalico Documentation Server Launcher (Windows)
:: Usage: double-click this file or run: docs_server.bat [port]
setlocal

set PORT=8800
if not "%1"=="" set PORT=%1

echo =============================================
echo   Kalico Documentation Server
echo   Port: %PORT%
echo =============================================
echo.
echo Place .md files in: docs\
echo Translations in: docs\zh\  docs\de\  etc.
echo   or in: docs\i18n\simple-chinese\  etc.
echo.
echo Opening http://127.0.0.1:%PORT% in browser...
start http://127.0.0.1:%PORT%

python "%~dp0docs_server.py" --port %PORT%
pause
