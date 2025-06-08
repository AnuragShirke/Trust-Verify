#!/bin/sh

# Start Redis consumer in the background
python redis_consumer.py &
REDIS_PID=$!

# Start the FastAPI server with uvicorn
python -m uvicorn dashboard_server:app --host 0.0.0.0 --port $PORT --workers 4 &
UVICORN_PID=$!

# Function to handle shutdown
cleanup() {
    echo "Shutting down services..."
    kill $REDIS_PID
    kill $UVICORN_PID
    exit 0
}

# Set up signal handling
trap cleanup SIGTERM SIGINT

# Wait for either process to exit
wait $REDIS_PID $UVICORN_PID
