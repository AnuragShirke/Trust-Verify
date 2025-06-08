#!/bin/bash

# Start Redis consumer in the background
python redis_consumer.py &

# Start dashboard server with proper port binding
python -m gunicorn dashboard_server:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:$PORT \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info
