FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the API application
COPY . .

# Create necessary directories
RUN mkdir -p /app/data/models /app/cache /app/model /app/mlops

# Generate sample model files
RUN python generate_models.py

# Set Python path to include parent directory for MLOps imports
ENV PYTHONPATH="${PYTHONPATH}:/app:/app/.."

# Expose the port the app runs on
EXPOSE 8000

# Create a startup script to handle environment variables
RUN echo '#!/bin/bash\n\
PORT="${PORT:-8000}"\n\
echo "Starting server on port $PORT"\n\
exec uvicorn main:app --host 0.0.0.0 --port $PORT\n\
' > /app/start.sh && chmod +x /app/start.sh

# Command to run the application
# In production, we don't use --reload for better performance
CMD ["/app/start.sh"]
