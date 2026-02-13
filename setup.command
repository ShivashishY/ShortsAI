#!/bin/bash
#
# YouTube to Shorts AI Generator - Setup Script
# Supports: macOS and Linux
# This script installs all dependencies and runs the project automatically
#
# VERBOSE MODE ENABLED - All commands and outputs are displayed
#

set -e

# Enable verbose mode - show all commands being executed
set -x

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Logging functions with timestamps
log_info() { set +x; echo -e "${BLUE}[INFO $(date '+%H:%M:%S')]${NC} $1"; set -x; }
log_success() { set +x; echo -e "${GREEN}[SUCCESS $(date '+%H:%M:%S')]${NC} $1"; set -x; }
log_warning() { set +x; echo -e "${YELLOW}[WARNING $(date '+%H:%M:%S')]${NC} $1"; set -x; }
log_error() { set +x; echo -e "${RED}[ERROR $(date '+%H:%M:%S')]${NC} $1"; set -x; }
log_step() { set +x; echo -e "${CYAN}[STEP $(date '+%H:%M:%S')]${NC} $1"; set -x; }
log_debug() { set +x; echo -e "${MAGENTA}[DEBUG $(date '+%H:%M:%S')]${NC} $1"; set -x; }
log_cmd() { set +x; echo -e "${YELLOW}[CMD]${NC} $1"; set -x; }

# Detect OS
detect_os() {
    log_debug "OSTYPE = $OSTYPE"
    log_debug "Checking operating system..."
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        log_info "Detected macOS"
        log_debug "macOS version: $(sw_vers -productVersion 2>/dev/null || echo 'unknown')"
        log_debug "Architecture: $(uname -m)"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
        log_debug "Kernel: $(uname -r)"
        # Detect Linux distribution
        if [ -f /etc/os-release ]; then
            . /etc/os-release
            DISTRO=$ID
            log_info "Detected Linux ($DISTRO)"
            log_debug "Distribution details: $PRETTY_NAME"
        else
            DISTRO="unknown"
            log_info "Detected Linux (unknown distribution)"
        fi
    else
        log_error "Unsupported operating system: $OSTYPE"
        exit 1
    fi
    
    log_debug "Working directory: $(pwd)"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Install Homebrew (macOS)
install_homebrew() {
    log_debug "Checking for Homebrew..."
    if [[ "$OS" == "macos" ]] && ! command_exists brew; then
        log_step "Installing Homebrew..."
        log_cmd "curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh | /bin/bash"
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        
        # Add Homebrew to PATH for Apple Silicon
        if [[ -f /opt/homebrew/bin/brew ]]; then
            log_debug "Adding Homebrew to PATH for Apple Silicon..."
            eval "$(/opt/homebrew/bin/brew shellenv)"
        fi
        log_success "Homebrew installed"
        log_debug "Homebrew location: $(which brew)"
    else
        log_info "Homebrew is already installed at $(which brew 2>/dev/null || echo 'N/A')"
        log_debug "Homebrew version: $(brew --version 2>/dev/null | head -1 || echo 'unknown')"
    fi
}

# Install Python
install_python() {
    log_debug "Checking for Python 3..."
    if command_exists python3; then
        PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
        log_info "Python $PYTHON_VERSION is already installed"
        log_debug "Python location: $(which python3)"
        log_debug "Full version: $(python3 --version 2>&1)"
    else
        log_step "Installing Python..."
        if [[ "$OS" == "macos" ]]; then
            log_cmd "brew install python@3.11"
            brew install python@3.11
        elif [[ "$OS" == "linux" ]]; then
            if [[ "$DISTRO" == "ubuntu" || "$DISTRO" == "debian" ]]; then
                log_cmd "sudo apt-get update && sudo apt-get install -y python3 python3-pip python3-venv"
                sudo apt-get update
                sudo apt-get install -y python3 python3-pip python3-venv
            elif [[ "$DISTRO" == "fedora" ]]; then
                log_cmd "sudo dnf install -y python3 python3-pip"
                sudo dnf install -y python3 python3-pip
            elif [[ "$DISTRO" == "arch" ]]; then
                log_cmd "sudo pacman -S --noconfirm python python-pip"
                sudo pacman -S --noconfirm python python-pip
            else
                log_error "Unsupported Linux distribution for automatic Python installation"
                log_info "Please install Python 3.11+ manually and re-run this script"
                exit 1
            fi
        fi
        log_success "Python installed"
        log_debug "Python location: $(which python3)"
    fi
}

# Install Node.js
install_nodejs() {
    log_debug "Checking for Node.js..."
    if command_exists node; then
        NODE_VERSION=$(node --version)
        log_info "Node.js $NODE_VERSION is already installed"
        log_debug "Node location: $(which node)"
        log_debug "npm version: $(npm --version 2>/dev/null || echo 'not found')"
    else
        log_step "Installing Node.js..."
        if [[ "$OS" == "macos" ]]; then
            log_cmd "brew install node"
            brew install node
        elif [[ "$OS" == "linux" ]]; then
            if [[ "$DISTRO" == "ubuntu" || "$DISTRO" == "debian" ]]; then
                # Install Node.js via NodeSource
                log_cmd "curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -"
                curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
                log_cmd "sudo apt-get install -y nodejs"
                sudo apt-get install -y nodejs
            elif [[ "$DISTRO" == "fedora" ]]; then
                log_cmd "sudo dnf install -y nodejs npm"
                sudo dnf install -y nodejs npm
            elif [[ "$DISTRO" == "arch" ]]; then
                log_cmd "sudo pacman -S --noconfirm nodejs npm"
                sudo pacman -S --noconfirm nodejs npm
            else
                log_error "Unsupported Linux distribution for automatic Node.js installation"
                log_info "Please install Node.js 18+ manually and re-run this script"
                exit 1
            fi
        fi
        log_success "Node.js installed"
        log_debug "Node location: $(which node)"
        log_debug "Node version: $(node --version)"
    fi
}

# Install FFmpeg and audio libraries
install_ffmpeg() {
    log_debug "Checking for FFmpeg..."
    if command_exists ffmpeg; then
        FFMPEG_VERSION=$(ffmpeg -version 2>&1 | head -n1)
        log_info "FFmpeg is already installed"
        log_debug "$FFMPEG_VERSION"
    else
        log_step "Installing FFmpeg..."
        if [[ "$OS" == "macos" ]]; then
            log_cmd "brew install ffmpeg"
            brew install ffmpeg
        elif [[ "$OS" == "linux" ]]; then
            if [[ "$DISTRO" == "ubuntu" || "$DISTRO" == "debian" ]]; then
                log_cmd "sudo apt-get install -y ffmpeg"
                sudo apt-get update
                sudo apt-get install -y ffmpeg
            elif [[ "$DISTRO" == "fedora" ]]; then
                log_cmd "sudo dnf install -y ffmpeg"
                sudo dnf install -y ffmpeg
            elif [[ "$DISTRO" == "arch" ]]; then
                log_cmd "sudo pacman -S --noconfirm ffmpeg"
                sudo pacman -S --noconfirm ffmpeg
            else
                log_error "Unsupported Linux distribution for automatic FFmpeg installation"
                log_info "Please install FFmpeg manually and re-run this script"
                exit 1
            fi
        fi
        log_success "FFmpeg installed"
    fi
    
    # Install libsndfile for audio processing (required by soundfile/librosa)
    log_debug "Checking for libsndfile..."
    if [[ "$OS" == "macos" ]]; then
        if ! brew list libsndfile &>/dev/null; then
            log_step "Installing libsndfile for audio processing..."
            log_cmd "brew install libsndfile"
            brew install libsndfile
            log_success "libsndfile installed"
        else
            log_info "libsndfile is already installed"
        fi
    elif [[ "$OS" == "linux" ]]; then
        if ! ldconfig -p 2>/dev/null | grep -q libsndfile || ! dpkg -l libsndfile1 &>/dev/null; then
            log_step "Installing libsndfile for audio processing..."
            if [[ "$DISTRO" == "ubuntu" || "$DISTRO" == "debian" ]]; then
                log_cmd "sudo apt-get install -y libsndfile1"
                sudo apt-get install -y libsndfile1
            elif [[ "$DISTRO" == "fedora" ]]; then
                log_cmd "sudo dnf install -y libsndfile"
                sudo dnf install -y libsndfile
            elif [[ "$DISTRO" == "arch" ]]; then
                log_cmd "sudo pacman -S --noconfirm libsndfile"
                sudo pacman -S --noconfirm libsndfile
            fi
            log_success "libsndfile installed"
        else
            log_info "libsndfile is already installed"
        fi
    fi
}

# Install Ollama
install_ollama() {
    if command_exists ollama; then
        log_info "Ollama is already installed"
    else
        log_step "Installing Ollama..."
        if [[ "$OS" == "macos" ]]; then
            brew install ollama
        elif [[ "$OS" == "linux" ]]; then
            curl -fsSL https://ollama.com/install.sh | sh
        fi
        log_success "Ollama installed"
    fi
}

# Start Ollama server
start_ollama() {
    log_step "Starting Ollama server..."
    
    # Check if Ollama is already running
    log_debug "Checking if Ollama is already running on port 11434..."
    if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
        log_info "Ollama server is already running"
        log_debug "Ollama models: $(ollama list 2>&1 || echo 'unable to list')"
    else
        # Start Ollama in background
        log_debug "Starting Ollama server process..."
        if [[ "$OS" == "macos" ]]; then
            log_cmd "ollama serve &"
            ollama serve 2>&1 &
        else
            log_cmd "nohup ollama serve &"
            nohup ollama serve 2>&1 &
        fi
        
        # Wait for Ollama to start
        log_info "Waiting for Ollama server to start..."
        for i in {1..30}; do
            if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
                log_success "Ollama server started"
                break
            fi
            sleep 1
        done
        
        if ! curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
            log_warning "Ollama server may not have started properly"
        fi
    fi
}

# Pull LLaVA model
pull_llava_model() {
    log_step "Checking/Pulling LLaVA model for AI content analysis..."
    
    # Check if model already exists
    log_debug "Checking existing Ollama models..."
    log_cmd "ollama list"
    ollama list 2>&1 || true
    
    if ollama list 2>/dev/null | grep -q "llava"; then
        log_info "LLaVA model is already downloaded"
        log_debug "Model details:"
        ollama show llava 2>&1 || true
    else
        log_info "Downloading LLaVA model (~4.7GB)... This may take a while."
        log_cmd "ollama pull llava"
        ollama pull llava
        log_success "LLaVA model downloaded"
        log_debug "Verifying model:"
        ollama list 2>&1 || true
    fi
}

# Setup backend
setup_backend() {
    log_step "Setting up backend..."
    
    cd backend
    
    # Create virtual environment
    if [ ! -d "venv" ]; then
        log_info "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    log_debug "Upgrading pip..."
    log_cmd "pip install --upgrade pip"
    pip install --upgrade pip
    
    # Install requirements
    log_info "Installing Python dependencies..."
    log_debug "Reading requirements from requirements.txt:"
    cat requirements.txt
    log_cmd "pip install -r requirements.txt"
    pip install -r requirements.txt
    
    log_success "Backend setup complete"
    cd ..
}

# Setup frontend
setup_frontend() {
    log_step "Setting up frontend..."
    
    cd frontend
    
    # Install npm dependencies
    log_info "Installing npm dependencies..."
    log_debug "Reading package.json dependencies:"
    cat package.json | grep -A 20 '"dependencies"' || true
    log_cmd "npm install"
    npm install
    
    log_success "Frontend setup complete"
    cd ..
}

# Run the project
run_project() {
    log_step "Starting the project..."
    
    echo ""
    echo -e "${GREEN}============================================${NC}"
    echo -e "${GREEN}   YouTube to Shorts AI Generator${NC}"
    echo -e "${GREEN}============================================${NC}"
    echo ""
    
    # Start backend in background
    log_info "Starting backend server on http://localhost:8000..."
    cd backend
    source venv/bin/activate
    log_debug "Python executable: $(which python)"
    log_debug "Pip packages installed:"
    pip list
    log_cmd "uvicorn server:app --reload --host 0.0.0.0 --port 8000 --log-level debug"
    uvicorn server:app --reload --host 0.0.0.0 --port 8000 --log-level debug &
    BACKEND_PID=$!
    log_debug "Backend PID: $BACKEND_PID"
    cd ..
    
    # Wait for backend to start
    log_debug "Waiting for backend to start (3 seconds)..."
    sleep 3
    
    # Start frontend
    log_info "Starting frontend server on http://localhost:3000..."
    cd frontend
    log_debug "Node version: $(node --version)"
    log_debug "npm version: $(npm --version)"
    log_cmd "npm run dev"
    npm run dev &
    FRONTEND_PID=$!
    log_debug "Frontend PID: $FRONTEND_PID"
    cd ..
    
    # Wait a bit for frontend to start
    sleep 3
    
    echo ""
    echo -e "${GREEN}============================================${NC}"
    echo -e "${GREEN}   Application is running!${NC}"
    echo -e "${GREEN}============================================${NC}"
    echo ""
    echo -e "  ${CYAN}Frontend:${NC}  http://localhost:3000"
    echo -e "  ${CYAN}Backend:${NC}   http://localhost:8000"
    echo -e "  ${CYAN}API Docs:${NC}  http://localhost:8000/docs"
    echo ""
    echo -e "  Press ${YELLOW}Ctrl+C${NC} to stop all servers"
    echo ""
    
    # Open browser (optional)
    if [[ "$OS" == "macos" ]]; then
        log_debug "Opening browser on macOS..."
        sleep 2
        log_cmd "open http://localhost:3000"
        open http://localhost:3000 || log_warning "Could not open browser automatically"
    elif [[ "$OS" == "linux" ]]; then
        log_debug "Opening browser on Linux..."
        sleep 2
        log_cmd "xdg-open http://localhost:3000"
        xdg-open http://localhost:3000 || log_warning "Could not open browser automatically"
    fi
    
    # Wait for Ctrl+C
    trap cleanup SIGINT SIGTERM
    wait
}

# Cleanup function
cleanup() {
    echo ""
    log_info "Shutting down servers..."
    
    # Kill backend
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    
    # Kill frontend
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    
    # Kill any remaining node/python processes for this project
    pkill -f "uvicorn server:app" 2>/dev/null || true
    pkill -f "vite" 2>/dev/null || true
    
    log_success "Servers stopped"
    exit 0
}

# Main function
main() {
    echo ""
    echo -e "${CYAN}============================================${NC}"
    echo -e "${CYAN}   YouTube to Shorts AI Generator Setup${NC}"
    echo -e "${CYAN}============================================${NC}"
    echo ""
    
    # Get the script's directory
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    cd "$SCRIPT_DIR"
    
    # Detect operating system
    detect_os
    
    # Install dependencies
    if [[ "$OS" == "macos" ]]; then
        install_homebrew
    fi
    
    install_python
    install_nodejs
    install_ffmpeg
    install_ollama
    
    # Start Ollama and pull model
    start_ollama
    pull_llava_model
    
    # Setup project
    setup_backend
    setup_frontend
    
    echo ""
    log_success "All dependencies installed successfully!"
    echo ""
    
    # Run the project
    run_project
}

# Run main function
main "$@"
