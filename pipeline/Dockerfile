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
# Install lxml with html_clean separately first
RUN pip install --no-cache-dir lxml_html_clean
# Then install the rest of the requirements
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create necessary directories
RUN mkdir -p /app/data /app/logs /app/results

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=10000
ENV WEB_CONCURRENCY=2

# Expose the port
EXPOSE ${PORT}

# Command to run both services
CMD ["sh", "-c", "python redis_consumer.py & gunicorn dashboard_server:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --timeout 300 --keep-alive 120 --access-logfile - --error-logfile -"]
