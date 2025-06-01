#!/bin/bash

# Start API in background
echo "Starting FastAPI server..."
uvicorn api:app --host 0.0.0.0 --port 8687 --reload &

# Wait a moment for the API to start
sleep 120

# Start Streamlit in foreground
echo "Starting Streamlit app..."
streamlit run app.py --server.port 8585 --server.address 0.0.0.0