@echo off
SETLOCAL ENABLEDELAYEDEXPANSION
REM YouTube to Shorts AI Generator - Quick Start
REM Use this to run the project after setup is complete
REM VERBOSE MODE ENABLED - All commands and outputs are displayed

echo.
echo ============================================
echo    YouTube to Shorts AI Generator
echo ============================================
echo    VERBOSE LOGGING ENABLED
echo ============================================
echo.

cd /d "%~dp0"
echo [DEBUG %TIME%] Script directory: %~dp0
echo [DEBUG %TIME%] Current directory: %CD%

REM System info
echo [DEBUG %TIME%] Checking system info...
echo [DEBUG %TIME%] Windows version:
ver
echo.

REM Check if Ollama is running
echo [INFO %TIME%] Checking Ollama server status...
curl -s http://localhost:11434/api/tags >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [INFO %TIME%] Starting Ollama server...
    echo [CMD] ollama serve
    start "" ollama serve
    echo [DEBUG %TIME%] Waiting 3 seconds for Ollama to start...
    timeout /t 3 /nobreak
    echo [DEBUG %TIME%] Listing Ollama models:
    ollama list
) else (
    echo [INFO %TIME%] Ollama server is already running
    echo [DEBUG %TIME%] Ollama models:
    ollama list
)

echo.

REM Start backend
echo [INFO %TIME%] Starting backend server on http://localhost:8000...
cd backend
echo [DEBUG %TIME%] Changed to backend directory: %CD%
echo [CMD] venv\Scripts\activate
echo [DEBUG %TIME%] Starting uvicorn with debug logging...
echo [CMD] uvicorn server:app --reload --host 0.0.0.0 --port 8000 --log-level debug
start "Backend" cmd /k "venv\Scripts\activate && pip list && uvicorn server:app --reload --host 0.0.0.0 --port 8000 --log-level debug"
cd ..

echo [DEBUG %TIME%] Waiting 2 seconds for backend to initialize...
timeout /t 2 /nobreak

REM Start frontend
echo [INFO %TIME%] Starting frontend server on http://localhost:3000...
cd frontend
echo [DEBUG %TIME%] Changed to frontend directory: %CD%
echo [DEBUG %TIME%] Node version:
node --version
echo [DEBUG %TIME%] npm version:
npm --version
echo [CMD] npm run dev
start "Frontend" cmd /k "npm run dev"
cd ..

echo [DEBUG %TIME%] Waiting 3 seconds for frontend to initialize...
timeout /t 3 /nobreak

echo.
echo ============================================
echo    Application is running!
echo ============================================
echo.
echo   Frontend:  http://localhost:3000
echo   Backend:   http://localhost:8000
echo   API Docs:  http://localhost:8000/docs
echo.

REM Open browser
echo [DEBUG %TIME%] Opening browser...
echo [CMD] start http://localhost:3000
start http://localhost:3000

echo.
echo [INFO %TIME%] Servers are running in separate windows
echo [INFO %TIME%] Close this window to stop monitoring
echo [INFO %TIME%] Close Backend/Frontend windows to stop servers
echo.
echo Press any key to stop ALL servers...
pause

REM Stop servers
echo.
echo [INFO %TIME%] Shutting down servers...
echo [DEBUG %TIME%] Killing node.exe processes...
echo [CMD] taskkill /f /im node.exe
taskkill /f /im node.exe 2>&1
echo [DEBUG %TIME%] Killing python/uvicorn processes...
echo [CMD] taskkill /f /im python.exe
taskkill /f /im python.exe 2>&1
echo [DEBUG %TIME%] Killing Backend window...
echo [CMD] taskkill /f /fi "WINDOWTITLE eq Backend"
taskkill /f /fi "WINDOWTITLE eq Backend" 2>&1
echo [DEBUG %TIME%] Killing Frontend window...
echo [CMD] taskkill /f /fi "WINDOWTITLE eq Frontend"
taskkill /f /fi "WINDOWTITLE eq Frontend" 2>&1

echo.
echo [SUCCESS %TIME%] Servers stopped
echo.
pause
