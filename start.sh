#!/bin/bash
#
# YouTube to Shorts AI Generator - Quick Start Script
# Use this to run the project after setup is complete
# VERBOSE MODE ENABLED - All commands and outputs are displayed
#

set -e

# Enable verbose mode - show all commands being executed
set -x

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m'

# Logging functions with timestamps
log_info() { set +x; echo -e "${BLUE}[INFO $(date '+%H:%M:%S')]${NC} $1"; set -x; }
log_success() { set +x; echo -e "${GREEN}[SUCCESS $(date '+%H:%M:%S')]${NC} $1"; set -x; }
log_warning() { set +x; echo -e "${YELLOW}[WARNING $(date '+%H:%M:%S')]${NC} $1"; set -x; }
log_error() { set +x; echo -e "${RED}[ERROR $(date '+%H:%M:%S')]${NC} $1"; set -x; }
log_debug() { set +x; echo -e "${MAGENTA}[DEBUG $(date '+%H:%M:%S')]${NC} $1"; set -x; }
log_cmd() { set +x; echo -e "${YELLOW}[CMD]${NC} $1"; set -x; }

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

log_debug "Script directory: $SCRIPT_DIR"
log_debug "Current working directory: $(pwd)"

echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}   YouTube to Shorts AI Generator${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""

# Check system info
log_debug "OS Type: $OSTYPE"
log_debug "Shell: $SHELL"
log_debug "Date: $(date)"

# Start Ollama if not running
log_info "Checking Ollama server status..."
if ! curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
    log_info "Starting Ollama server..."
    log_cmd "ollama serve &"
    ollama serve 2>&1 &
    log_debug "Waiting 3 seconds for Ollama to start..."
    sleep 3
    log_debug "Ollama models available:"
    ollama list 2>&1 || log_warning "Could not list Ollama models"
else
    log_info "Ollama server is already running"
    log_debug "Ollama models:"
    ollama list 2>&1 || true
fi

# Start backend
log_info "Starting backend server..."
cd backend
log_debug "Changed to backend directory: $(pwd)"
log_cmd "source venv/bin/activate"
source venv/bin/activate
log_debug "Python executable: $(which python)"
log_debug "Python version: $(python --version)"
log_debug "Installed packages:"
pip list
log_cmd "uvicorn server:app --reload --host 0.0.0.0 --port 8000 --log-level debug"
uvicorn server:app --reload --host 0.0.0.0 --port 8000 --log-level debug &
BACKEND_PID=$!
log_debug "Backend PID: $BACKEND_PID"
cd ..

log_debug "Waiting 2 seconds for backend to initialize..."
sleep 2

# Start frontend
log_info "Starting frontend server..."
cd frontend
log_debug "Changed to frontend directory: $(pwd)"
log_debug "Node version: $(node --version)"
log_debug "npm version: $(npm --version)"
log_cmd "npm run dev"
npm run dev &
FRONTEND_PID=$!
log_debug "Frontend PID: $FRONTEND_PID"
cd ..

log_debug "Waiting 3 seconds for frontend to initialize..."
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
echo -e "  ${MAGENTA}Backend PID:${NC}  $BACKEND_PID"
echo -e "  ${MAGENTA}Frontend PID:${NC} $FRONTEND_PID"
echo ""
echo -e "  Press ${YELLOW}Ctrl+C${NC} to stop all servers"
echo ""

# Open browser
if [[ "$OSTYPE" == "darwin"* ]]; then
    log_debug "Opening browser on macOS..."
    log_cmd "open http://localhost:3000"
    open http://localhost:3000 || log_warning "Could not open browser automatically"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    log_debug "Opening browser on Linux..."
    log_cmd "xdg-open http://localhost:3000"
    xdg-open http://localhost:3000 || log_warning "Could not open browser automatically"
fi

# Cleanup on exit
cleanup() {
    echo ""
    log_info "Shutting down servers..."
    log_debug "Killing backend PID: $BACKEND_PID"
    kill $BACKEND_PID 2>/dev/null || true
    log_debug "Killing frontend PID: $FRONTEND_PID"
    kill $FRONTEND_PID 2>/dev/null || true
    log_debug "Killing any remaining uvicorn processes..."
    pkill -f "uvicorn server:app" 2>/dev/null || true
    log_debug "Killing any remaining vite processes..."
    pkill -f "vite" 2>/dev/null || true
    log_success "Servers stopped"
    exit 0
}

trap cleanup SIGINT SIGTERM
log_debug "Trap set for SIGINT and SIGTERM"
log_info "Servers are running. Monitoring logs..."
wait
