# YouTube to Shorts AI Generator - Windows Setup Script
# This script installs all dependencies and runs the project automatically
# Run with: .\setup.ps1 (as Administrator recommended)

# Enable strict mode
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Colors and formatting
function Write-Info { param($msg) Write-Host "[INFO] " -ForegroundColor Blue -NoNewline; Write-Host $msg }
function Write-Success { param($msg) Write-Host "[SUCCESS] " -ForegroundColor Green -NoNewline; Write-Host $msg }
function Write-Warning { param($msg) Write-Host "[WARNING] " -ForegroundColor Yellow -NoNewline; Write-Host $msg }
function Write-Error { param($msg) Write-Host "[ERROR] " -ForegroundColor Red -NoNewline; Write-Host $msg }
function Write-Step { param($msg) Write-Host "[STEP] " -ForegroundColor Cyan -NoNewline; Write-Host $msg }

# Check if running as administrator
function Test-Administrator {
    $currentUser = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
    return $currentUser.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Check if command exists
function Test-Command {
    param($Command)
    $null -ne (Get-Command $Command -ErrorAction SilentlyContinue)
}

# Install Chocolatey
function Install-Chocolatey {
    if (-not (Test-Command choco)) {
        Write-Step "Installing Chocolatey package manager..."
        Set-ExecutionPolicy Bypass -Scope Process -Force
        [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
        Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
        
        # Refresh environment
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
        Write-Success "Chocolatey installed"
    } else {
        Write-Info "Chocolatey is already installed"
    }
}

# Install Python
function Install-Python {
    if (Test-Command python) {
        $version = python --version 2>&1
        Write-Info "Python is already installed: $version"
    } else {
        Write-Step "Installing Python..."
        choco install python311 -y
        
        # Refresh environment
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
        Write-Success "Python installed"
    }
}

# Install Node.js
function Install-NodeJS {
    if (Test-Command node) {
        $version = node --version 2>&1
        Write-Info "Node.js is already installed: $version"
    } else {
        Write-Step "Installing Node.js..."
        choco install nodejs-lts -y
        
        # Refresh environment
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
        Write-Success "Node.js installed"
    }
}

# Install FFmpeg
function Install-FFmpeg {
    if (Test-Command ffmpeg) {
        Write-Info "FFmpeg is already installed"
    } else {
        Write-Step "Installing FFmpeg..."
        choco install ffmpeg -y
        
        # Refresh environment
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
        Write-Success "FFmpeg installed"
    }
}

# Install Ollama
function Install-Ollama {
    if (Test-Command ollama) {
        Write-Info "Ollama is already installed"
    } else {
        Write-Step "Installing Ollama..."
        
        # Download Ollama installer
        $ollamaUrl = "https://ollama.com/download/OllamaSetup.exe"
        $ollamaInstaller = "$env:TEMP\OllamaSetup.exe"
        
        Write-Info "Downloading Ollama..."
        Invoke-WebRequest -Uri $ollamaUrl -OutFile $ollamaInstaller
        
        Write-Info "Running Ollama installer..."
        Start-Process -FilePath $ollamaInstaller -ArgumentList "/S" -Wait
        
        # Refresh environment
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
        
        # Add Ollama to path if not already there
        $ollamaPath = "$env:LOCALAPPDATA\Programs\Ollama"
        if (Test-Path $ollamaPath) {
            $env:Path += ";$ollamaPath"
        }
        
        Write-Success "Ollama installed"
    }
}

# Start Ollama server
function Start-OllamaServer {
    Write-Step "Starting Ollama server..."
    
    # Check if already running
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -Method Get -ErrorAction Stop
        Write-Info "Ollama server is already running"
        return
    } catch {
        # Not running, start it
    }
    
    # Start Ollama in background
    Start-Process -FilePath "ollama" -ArgumentList "serve" -WindowStyle Hidden
    
    # Wait for server to start
    Write-Info "Waiting for Ollama server to start..."
    $maxAttempts = 30
    for ($i = 0; $i -lt $maxAttempts; $i++) {
        try {
            $response = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -Method Get -ErrorAction Stop
            Write-Success "Ollama server started"
            return
        } catch {
            Start-Sleep -Seconds 1
        }
    }
    
    Write-Warning "Ollama server may not have started properly"
}

# Pull LLaVA model
function Get-LlavaModel {
    Write-Step "Checking/Pulling LLaVA model for AI content analysis..."
    
    try {
        $models = ollama list 2>&1
        if ($models -match "llava") {
            Write-Info "LLaVA model is already downloaded"
            return
        }
    } catch {}
    
    Write-Info "Downloading LLaVA model (~4.7GB)... This may take a while."
    ollama pull llava
    Write-Success "LLaVA model downloaded"
}

# Setup backend
function Setup-Backend {
    Write-Step "Setting up backend..."
    
    Push-Location backend
    
    # Create virtual environment
    if (-not (Test-Path "venv")) {
        Write-Info "Creating Python virtual environment..."
        python -m venv venv
    }
    
    # Activate virtual environment
    & .\venv\Scripts\Activate.ps1
    
    # Upgrade pip
    python -m pip install --upgrade pip 2>&1 | Out-Null
    
    # Install requirements
    Write-Info "Installing Python dependencies..."
    pip install -r requirements.txt
    
    Write-Success "Backend setup complete"
    Pop-Location
}

# Setup frontend
function Setup-Frontend {
    Write-Step "Setting up frontend..."
    
    Push-Location frontend
    
    # Install npm dependencies
    Write-Info "Installing npm dependencies..."
    npm install
    
    Write-Success "Frontend setup complete"
    Pop-Location
}

# Run project
function Start-Project {
    Write-Step "Starting the project..."
    
    Write-Host ""
    Write-Host "============================================" -ForegroundColor Green
    Write-Host "   YouTube to Shorts AI Generator" -ForegroundColor Green
    Write-Host "============================================" -ForegroundColor Green
    Write-Host ""
    
    # Start backend
    Write-Info "Starting backend server on http://localhost:8000..."
    
    Push-Location backend
    $backendProcess = Start-Process -FilePath "cmd" -ArgumentList "/c", "venv\Scripts\activate && uvicorn server:app --reload --host 0.0.0.0 --port 8000" -PassThru -WindowStyle Minimized
    Pop-Location
    
    Start-Sleep -Seconds 3
    
    # Start frontend
    Write-Info "Starting frontend server on http://localhost:3000..."
    
    Push-Location frontend
    $frontendProcess = Start-Process -FilePath "cmd" -ArgumentList "/c", "npm run dev" -PassThru -WindowStyle Minimized
    Pop-Location
    
    Start-Sleep -Seconds 3
    
    Write-Host ""
    Write-Host "============================================" -ForegroundColor Green
    Write-Host "   Application is running!" -ForegroundColor Green
    Write-Host "============================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "  Frontend:  " -ForegroundColor Cyan -NoNewline; Write-Host "http://localhost:3000"
    Write-Host "  Backend:   " -ForegroundColor Cyan -NoNewline; Write-Host "http://localhost:8000"
    Write-Host "  API Docs:  " -ForegroundColor Cyan -NoNewline; Write-Host "http://localhost:8000/docs"
    Write-Host ""
    Write-Host "  Press " -NoNewline; Write-Host "Ctrl+C" -ForegroundColor Yellow -NoNewline; Write-Host " to stop all servers"
    Write-Host ""
    
    # Open browser
    Start-Sleep -Seconds 2
    Start-Process "http://localhost:3000"
    
    # Wait for user to stop
    Write-Host "Press Enter to stop the servers..." -ForegroundColor Yellow
    Read-Host
    
    # Cleanup
    Write-Info "Shutting down servers..."
    
    if ($backendProcess -and !$backendProcess.HasExited) {
        Stop-Process -Id $backendProcess.Id -Force -ErrorAction SilentlyContinue
    }
    if ($frontendProcess -and !$frontendProcess.HasExited) {
        Stop-Process -Id $frontendProcess.Id -Force -ErrorAction SilentlyContinue
    }
    
    # Kill any remaining processes
    Get-Process -Name "node" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
    Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowTitle -eq "" } | Stop-Process -Force -ErrorAction SilentlyContinue
    
    Write-Success "Servers stopped"
}

# Main function
function Main {
    Write-Host ""
    Write-Host "============================================" -ForegroundColor Cyan
    Write-Host "   YouTube to Shorts AI Generator Setup" -ForegroundColor Cyan
    Write-Host "============================================" -ForegroundColor Cyan
    Write-Host ""
    
    # Check for admin privileges
    if (-not (Test-Administrator)) {
        Write-Warning "Running without administrator privileges. Some installations may fail."
        Write-Warning "Consider running PowerShell as Administrator for best results."
        Write-Host ""
    }
    
    # Get script directory
    $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
    if ([string]::IsNullOrEmpty($scriptDir)) {
        $scriptDir = Get-Location
    }
    Set-Location $scriptDir
    
    # Install dependencies
    Install-Chocolatey
    Install-Python
    Install-NodeJS
    Install-FFmpeg
    Install-Ollama
    
    # Refresh PATH
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    
    # Start Ollama and pull model
    Start-OllamaServer
    Get-LlavaModel
    
    # Setup project
    Setup-Backend
    Setup-Frontend
    
    Write-Host ""
    Write-Success "All dependencies installed successfully!"
    Write-Host ""
    
    # Run the project
    Start-Project
}

# Run main
Main
