#!/bin/bash
cd "$(dirname "$0")"

# Free ports in case of previous run
lsof -ti:8000 | xargs kill -9 2>/dev/null
lsof -ti:8501 | xargs kill -9 2>/dev/null
sleep 1

echo "🚀 Starting Student Housing app..."

# Ensure streamlit is installed
if ! python3 -c "import streamlit" 2>/dev/null; then
    echo "  → Installing streamlit..."
    pip3 install streamlit --user
fi

# Start backend in background
echo "  → Starting FastAPI backend (port 8000)..."
python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait for backend to be ready
sleep 2
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo "❌ Backend failed to start"
    exit 1
fi

echo "  ✓ Backend running at http://localhost:8000"
echo "  → Starting Streamlit frontend (port 8501)..."
echo ""

# Start frontend (blocks until Ctrl+C)
python3 -m streamlit run app.py --server.headless true

# When Streamlit exits, kill backend too
kill $BACKEND_PID 2>/dev/null
