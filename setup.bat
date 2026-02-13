@echo off
REM YouTube to Shorts AI Generator - Windows Setup
REM This batch file runs the PowerShell setup script

echo.
echo ============================================
echo    YouTube to Shorts AI Generator Setup
echo ============================================
echo.

REM Check for PowerShell
where powershell >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] PowerShell is not available on this system.
    echo Please install PowerShell and try again.
    pause
    exit /b 1
)

REM Run PowerShell script with execution policy bypass
echo [INFO] Starting setup with PowerShell...
echo.

powershell -ExecutionPolicy Bypass -File "%~dp0setup.ps1"

if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] Setup failed. Please check the errors above.
    pause
    exit /b 1
)

pause
