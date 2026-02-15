#!/bin/bash

# Function to kill background processes on exit
cleanup() {
    echo "Stopping servers..."
    kill $(jobs -p) 2>/dev/null
}
trap cleanup EXIT

echo "Starting Salesvoice Backend (Token Server)..."
source backend/venv/bin/activate
uvicorn backend.main:app --reload --port 8000 &
BACKEND_PID=$!

echo "Starting Salesvoice Agent Worker..."
# The 'dev' command connects the worker to the LiveKit server
python backend/agent.py dev &
AGENT_PID=$!

echo "Starting Salesvoice Frontend..."
cd frontend
npm run dev &
FRONTEND_PID=$!

# Wait for all processes
wait $BACKEND_PID $AGENT_PID $FRONTEND_PID
