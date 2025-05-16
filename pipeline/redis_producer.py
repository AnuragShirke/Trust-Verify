#!/usr/bin/env python
"""
Redis Producer Script

This script reads collected news articles and pushes them to a Redis stream.
"""

import os
import json
import time
import logging
import datetime
import redis
from typing import List, Dict, Any, Optional
from glob import glob

# Configure logging
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/redis_producer.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("redis_producer")

# Redis configuration
REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
REDIS_DB = int(os.environ.get("REDIS_DB", 0))
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD", None)
REDIS_STREAM_NAME = os.environ.get("REDIS_STREAM_NAME", "news_articles")

def connect_to_redis() -> redis.Redis:
    """Connect to Redis server."""
    try:
        client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            password=REDIS_PASSWORD,
            decode_responses=True  # Automatically decode responses to strings
        )
        # Test connection
        client.ping()
        logger.info(f"Connected to Redis at {REDIS_HOST}:{REDIS_PORT}")
        return client
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {str(e)}")
        raise

def get_latest_article_file() -> Optional[str]:
    """Get the path to the latest article JSON file."""
    try:
        data_dir = "data"
        if not os.path.exists(data_dir):
            logger.warning(f"Data directory {data_dir} does not exist")
            return None

        # Find all article JSON files
        article_files = glob(f"{data_dir}/articles_*.json")
        if not article_files:
            logger.warning("No article files found")
            return None

        # Sort by modification time (newest first)
        latest_file = max(article_files, key=os.path.getmtime)
        logger.info(f"Latest article file: {latest_file}")
        return latest_file
    except Exception as e:
        logger.error(f"Error finding latest article file: {str(e)}")
        return None

def load_articles(file_path: str) -> List[Dict[str, Any]]:
    """Load articles from a JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            articles = json.load(f)
        logger.info(f"Loaded {len(articles)} articles from {file_path}")
        return articles
    except Exception as e:
        logger.error(f"Error loading articles from {file_path}: {str(e)}")
        return []

def publish_to_redis_stream(redis_client: redis.Redis, articles: List[Dict[str, Any]]) -> int:
    """Publish articles to Redis stream."""
    published_count = 0

    for article in articles:
        try:
            # Convert article to a flat dictionary with string values for Redis
            article_data = {}
            for key, value in article.items():
                if isinstance(value, (list, dict)):
                    article_data[key] = json.dumps(value)
                else:
                    article_data[key] = str(value) if value is not None else ""

            # Add a timestamp if not present
            if "timestamp" not in article_data:
                article_data["timestamp"] = datetime.datetime.now().isoformat()

            # Add to Redis stream
            redis_client.xadd(REDIS_STREAM_NAME, article_data)
            published_count += 1
            logger.debug(f"Published article: {article.get('title', 'Unknown')}")
        except Exception as e:
            logger.error(f"Error publishing article to Redis: {str(e)}")

    return published_count

def main():
    """Main function to publish articles to Redis stream."""
    logger.info("Starting Redis producer")

    try:
        # Connect to Redis
        redis_client = connect_to_redis()

        # Get the latest article file
        latest_file = get_latest_article_file()
        if not latest_file:
            logger.error("No article file found. Run news_collector.py first.")
            return

        # Load articles
        articles = load_articles(latest_file)
        if not articles:
            logger.error("No articles loaded. Check the article file.")
            return

        # Publish to Redis stream
        published_count = publish_to_redis_stream(redis_client, articles)
        logger.info(f"Published {published_count} articles to Redis stream '{REDIS_STREAM_NAME}'")

    except Exception as e:
        logger.error(f"Error in Redis producer: {str(e)}")

    logger.info("Redis producer completed")

if __name__ == "__main__":
    main()
