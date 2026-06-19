@echo off
echo Starting Kalico Documentation Site...
echo.
echo Available commands:
echo   npm run start      - Start English version
echo   npm run start:zh   - Start Chinese version
echo   npm run build      - Build for production
echo.

cd /d "%~dp0"

where node >nul 2>nul
if %errorlevel% neq 0 (
    echo Error: Node.js is not installed or not in PATH
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

if not exist "node_modules" (
    echo Installing dependencies...
    call npm install
    echo.
)

echo Starting Docusaurus development server...
echo Open http://localhost:3000 in your browser
echo.
call npm run start
