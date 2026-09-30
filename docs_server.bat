@echo off
:: Kalico Documentation Server Launcher (Windows)
:: Usage: double-click this file or run: docs_server.bat [port]
setlocal

set PORT=8800
if not "%1"=="" set PORT=%1

set VENV_PY=%~dp0docs\_kalico\.venv\Scripts\python.exe

echo =============================================
echo   Kalico Documentation Server (mkdocs serve)
echo   Port: %PORT%
echo =============================================
echo.
echo Opening http://127.0.0.1:%PORT%/ in browser...
echo.

if exist "%VENV_PY%" (
  "%VENV_PY%" "%~dp0docs_server.py" --port %PORT%
) else (
  python "%~dp0docs_server.py" --port %PORT%
)
pause
