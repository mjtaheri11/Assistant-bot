#!/bin/bash

# Exit immediately if a command fails
set -e

# Function to handle shutdown gracefully
cleanup() {
    echo "🛑 Shutting down services..."
    kill $API_PID $STREAMLIT_PID 2>/dev/null || true
    exit 0
}

# Set up signal handlers
trap cleanup SIGTERM SIGINT

# 1. Start api.py in the background
echo "✅ Starting api.py with Uvicorn..."
uvicorn api:app --host 0.0.0.0 --port 8689 --reload &
API_PID=$!

# 2. Wait for 30 sconds
echo "⏳ Waiting for 30 seconds..."
sleep 30

# 3. Start streamlit app in the background
echo "🚀 Starting app.py with Streamlit..."
streamlit run app.py --server.port 8585 --server.address 0.0.0.0 --server.baseUrlPath "${UI_BASE_PATH:-/}" &
STREAMLIT_PID=$!

# Wait for both processes
echo "📊 Both services are running. API PID: $API_PID, Streamlit PID: $STREAMLIT_PID"
wait