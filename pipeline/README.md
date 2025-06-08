# Real-Time News Analysis Pipeline

This directory contains the real-time news analysis pipeline for the Fake News Detector project.

## Overview

The pipeline consists of several components:

1. **News Collector**: Fetches news articles from RSS feeds and optionally from NewsAPI.
2. **Redis Producer**: Pushes collected articles to a Redis stream.
3. **Redis Consumer**: Processes articles from the Redis stream and analyzes them.
4. **Dashboard Server**: Provides a real-time dashboard with WebSocket support.
5. **Scheduler**: Runs the collector and producer at regular intervals.

## Requirements

- Python 3.8+
- Redis server
- Required Python packages (install with `pip install -r requirements.txt`):
  - feedparser
  - newspaper3k
  - redis
  - fastapi
  - uvicorn
  - loguru
  - schedule

## Setup

### Option 1: Using Docker (Recommended)

#### Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

#### Starting the Pipeline

1. Navigate to the pipeline directory:
   ```
   cd fake-news-detector/pipeline
   ```

2. Build and start the pipeline containers:
   ```
   docker-compose up
   ```

   This will start:
   - Redis server
   - Pipeline service (news collector, producer, consumer)
   - Dashboard service

3. The dashboard will be available at http://localhost:8080

#### Stopping the Pipeline

Press `Ctrl+C` in the terminal where the pipeline is running, or run:
```
docker-compose down
```

#### Running Individual Components

If you want to run specific components of the pipeline, you can override the default command:

```bash
# Run only the news collector
docker-compose run --rm pipeline python news_collector.py

# Run only the Redis producer
docker-compose run --rm pipeline python redis_producer.py

# Run only the Redis consumer
docker-compose run --rm pipeline python redis_consumer.py
```

### Option 2: Manual Setup

1. Install Redis:
   - **Windows**: Download and install from [Redis for Windows](https://github.com/microsoftarchive/redis/releases)
   - **Linux**: `sudo apt-get install redis-server`
   - **macOS**: `brew install redis`

2. Install Python dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Configure environment variables (optional):
   - `REDIS_HOST`: Redis server host (default: localhost)
   - `REDIS_PORT`: Redis server port (default: 6379)
   - `REDIS_PASSWORD`: Redis server password (default: None)
   - `NEWSAPI_KEY`: API key for NewsAPI (optional)

## Environment Variables Setup

For security reasons, sensitive configuration should be stored in environment variables, not in the code. Follow these steps:

1. Copy `.env.example` to create your `.env` file:
   ```bash
   cp .env.example .env
   ```

2. Update the `.env` file with your actual configuration:
   ```
   REDIS_HOST=your-redis-host
   REDIS_PORT=your-redis-port
   REDIS_PASSWORD=your-redis-password
   API_BASE_URL=your-api-url
   PORT=8080
   ```

⚠️ IMPORTANT: Never commit the `.env` file to version control. It contains sensitive information.

### Running the Pipeline Manually

#### Running Individual Components

1. **News Collector**:
   ```
   python news_collector.py
   ```

2. **Redis Producer**:
   ```
   python redis_producer.py
   ```

3. **Redis Consumer**:
   ```
   python redis_consumer.py
   ```

4. **Dashboard Server**:
   ```
   python dashboard_server.py
   ```

5. **Scheduler**:
   ```
   python scheduler.py
   ```

#### Running the Entire Pipeline

Use the `run_pipeline.py` script to run all components:

```
python run_pipeline.py --all
```

Or run specific components:

```
python run_pipeline.py --collector --producer --consumer
```

## Dashboard

The dashboard is available at `http://localhost:8080` when the dashboard server is running.

## Directory Structure

- `news_collector.py`: Collects news articles from RSS feeds and NewsAPI
- `redis_producer.py`: Pushes articles to Redis stream
- `redis_consumer.py`: Processes articles from Redis stream
- `dashboard_server.py`: Real-time dashboard with WebSocket support
- `realtime_dashboard.py`: Real-time dashboard with Server-Sent Events
- `scheduler.py`: Runs collector and producer at regular intervals
- `logger.py`: Centralized logging configuration
- `run_pipeline.py`: Main script to run the pipeline
- `Dockerfile`: Docker configuration for pipeline
- `Dockerfile.dashboard`: Docker configuration for dashboard
- `docker-compose.yml`: Docker Compose for pipeline
- `data/`: Directory for collected articles
- `logs/`: Directory for log files
- `results/`: Directory for processed results

## Customization

- Edit `news_collector.py` to add or remove RSS feeds
- Adjust collection intervals in `scheduler.py`
- Modify the dashboard HTML in `dashboard_server.py`

## Troubleshooting

- Check log files in the `logs/` directory
- Ensure Redis server is running
- Verify network connectivity for RSS feeds and NewsAPI

## Next Steps

- Add more data sources
- Implement more sophisticated analysis
- Add user feedback mechanism
- Set up monitoring with Prometheus and Grafana
