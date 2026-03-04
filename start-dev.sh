#!/bin/bash

# Development startup script for Optik Platform
echo "🚀 Starting Optik Platform Development Environment..."

# Kill any existing processes
echo "🔄 Cleaning up existing processes..."
pkill -f "python.*main.py" 2>/dev/null || true
pkill -f "next.*dev" 2>/dev/null || true

# Start backend server
echo "🔧 Starting Backend API Server on port 8000..."
cd /home/kali/Dapp_Optik/optik-platform/backend
source venv/bin/activate
export PYTHONPATH="/home/kali/Dapp_Optik/optik-platform/backend:$PYTHONPATH"
python -c "
import sys
sys.path.insert(0, '/home/kali/Dapp_Optik/optik-platform/backend')
import uvicorn
from api.main import app
uvicorn.run(app, host='0.0.0.0', port=8000, reload=True)
" &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start frontend server
echo "🎨 Starting Frontend Development Server on port 3003..."
cd /home/kali/Dapp_Optik/optik-platform/apps
npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ Development servers started!"
echo "📡 Backend API: http://localhost:8000"
echo "🌐 Frontend: http://localhost:3003"
echo "📚 API Docs: http://localhost:8000/api/docs"
echo ""
echo "Press Ctrl+C to stop all servers"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping servers..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    echo "✅ All servers stopped"
    exit 0
}

# Trap Ctrl+C
trap cleanup INT

# Wait for processes
wait
