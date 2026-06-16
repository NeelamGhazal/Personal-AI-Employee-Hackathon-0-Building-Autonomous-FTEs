#!/bin/bash
# Personal AI Employee - Dashboard Startup Script
# Full-Time Equivalent Hackathon 0

echo "=============================================="
echo "   Personal AI Employee Dashboard"
echo "   Full-Time Equivalent Hackathon 0"
echo "=============================================="
echo ""

# Change to project directory
cd /mnt/e/Full-Time-Equivalent-Hackathon-0/Full-Time-Equivalent-0

# Install dependencies if needed
echo "📦 Checking dependencies..."
pip install fastapi uvicorn python-multipart --quiet --break-system-packages 2>/dev/null || pip install fastapi uvicorn python-multipart --quiet

# Kill any existing server on port 8000
echo "🔄 Checking for existing server..."
pkill -f "uvicorn api_server:app" 2>/dev/null || true
sleep 1

# Start the API server
echo "🚀 Starting API server..."
uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload &
SERVER_PID=$!

# Wait for server to start
echo "⏳ Waiting for server to start..."
sleep 3

# Check if server is running
if curl -s http://localhost:8000/api/status > /dev/null 2>&1; then
    echo ""
    echo "=============================================="
    echo "✅ Dashboard running at: http://localhost:8000"
    echo "📚 API Docs at: http://localhost:8000/docs"
    echo "=============================================="
    echo ""

    # Open in browser (WSL)
    explorer.exe http://localhost:8000 2>/dev/null || xdg-open http://localhost:8000 2>/dev/null || echo "Open http://localhost:8000 in your browser"

    echo "Press Ctrl+C to stop the server"

    # Keep script running
    wait $SERVER_PID
else
    echo "❌ Server failed to start"
    exit 1
fi
