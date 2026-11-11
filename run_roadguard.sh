#!/usr/bin/env bash

# ========================================================
# RoadGuard Unified Runner
# Launches FastAPI Backend (Port 8000) & Vite Frontend (Port 5173)
# ========================================================

set -e

# Change to project root directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

echo "========================================================"
echo " 🛣️  RoadGuard: Deep Learning Road Damage Platform"
echo "========================================================"

# 1. Check Python virtual environment
if [ ! -d ".venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r backend/requirements.txt
else
    source .venv/bin/activate
fi

# 2. Check model weights
if [ ! -f "ml/models/roadguard_yolov8n.pt" ]; then
    echo "Initializing PyTorch model weights..."
    python3 ml/inference/generate_test_samples.py
fi

# 3. Apply database migrations
echo "Verifying database migrations..."
PYTHONPATH=. YOLO_CONFIG_DIR=/tmp/ultralytics alembic upgrade head >/dev/null 2>&1 || true

# Function to clean up child processes on exit
cleanup() {
    echo ""
    echo "Shutting down RoadGuard services..."
    kill $(jobs -p) 2>/dev/null || true
    exit 0
}
trap cleanup SIGINT SIGTERM EXIT

# 4. Start FastAPI Backend
echo "Starting FastAPI Backend on http://localhost:8000..."
export PYTHONPATH=.
export YOLO_CONFIG_DIR=/tmp/ultralytics
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait for backend to be ready
sleep 2

# 5. Start Vite React Frontend
echo "Starting React Frontend on http://localhost:5173..."
cd frontend
npm run dev -- --host 0.0.0.0 --port 5173 &
FRONTEND_PID=$!
cd ..

echo ""
echo "========================================================"
echo " ✅ RoadGuard is running live!"
echo " 👉 Web Interface: http://localhost:5173"
echo " 👉 Backend API  : http://localhost:8000"
echo " 👉 Swagger Docs : http://localhost:8000/docs"
echo "========================================================"
echo "Press Ctrl+C to stop all services."
echo ""

# Keep running
wait

