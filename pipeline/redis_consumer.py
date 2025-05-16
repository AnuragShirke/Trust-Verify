#!/usr/bin/env python
"""
Redis Consumer Script

This script consumes news articles from a Redis stream, processes them,
and stores the results in the database.
"""

import os
import json
import time
import logging
import datetime
import redis
import requests
from typing import Dict, Any, Optional

# Configure logging
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/redis_consumer.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("redis_consumer")

# Redis configuration
REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
REDIS_DB = int(os.environ.get("REDIS_DB", 0))
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD", None)
REDIS_STREAM_NAME = os.environ.get("REDIS_STREAM_NAME", "news_articles")
REDIS_CONSUMER_GROUP = os.environ.get("REDIS_CONSUMER_GROUP", "news_processors")
REDIS_CONSUMER_NAME = os.environ.get("REDIS_CONSUMER_NAME", f"consumer-{os.getpid()}")

# API configuration
API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")

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

def setup_consumer_group(redis_client: redis.Redis) -> None:
    """Set up the consumer group if it doesn't exist."""
    try:
        # Check if the stream exists
        if not redis_client.exists(REDIS_STREAM_NAME):
            # Create the stream with a dummy message that we'll process and acknowledge
            redis_client.xadd(REDIS_STREAM_NAME, {"_init": "init"})
            logger.info(f"Created stream '{REDIS_STREAM_NAME}'")

        # Create the consumer group if it doesn't exist
        try:
            redis_client.xgroup_create(REDIS_STREAM_NAME, REDIS_CONSUMER_GROUP, id='0', mkstream=True)
            logger.info(f"Created consumer group '{REDIS_CONSUMER_GROUP}'")
        except redis.exceptions.ResponseError as e:
            if "BUSYGROUP" in str(e):
                logger.info(f"Consumer group '{REDIS_CONSUMER_GROUP}' already exists")
            else:
                raise
    except Exception as e:
        logger.error(f"Error setting up consumer group: {str(e)}")
        raise

def process_article(article_data: Dict[str, str]) -> Dict[str, Any]:
    """Process an article by sending it to the API for analysis."""
    try:
        # Extract the content
        content = article_data.get("content", "")
        if not content:
            content = article_data.get("full_text", "")

        if not content:
            logger.warning("Article has no content to analyze")
            return {"error": "No content to analyze"}

        # Call the API to analyze the content
        response = requests.post(
            f"{API_BASE_URL}/trust-score",
            json={"text": content}
        )

        if response.status_code == 200:
            analysis_result = response.json()

            # Combine the article data with the analysis result
            result = {
                "article": {
                    "title": article_data.get("title", ""),
                    "url": article_data.get("url", ""),
                    "source": article_data.get("source", ""),
                    "published_date": article_data.get("published_date", ""),
                    "collection_time": article_data.get("collection_time", ""),
                },
                "analysis": analysis_result,
                "processed_at": datetime.datetime.now().isoformat()
            }

            logger.info(f"Processed article: {article_data.get('title', 'Unknown')}")
            return result
        else:
            logger.error(f"API returned status code {response.status_code}")
            return {"error": f"API error: {response.status_code}"}
    except Exception as e:
        logger.error(f"Error processing article: {str(e)}")
        return {"error": str(e)}

def save_result_to_database(result: Dict[str, Any]) -> bool:
    """Save the processed result to the database."""
    try:
        # For now, we'll just save to a local file
        # In a real implementation, this would insert into a database

        # Create the output directory if it doesn't exist
        os.makedirs("results", exist_ok=True)

        # Generate a filename based on the current time
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"results/result_{timestamp}.json"

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        logger.info(f"Saved result to {filename}")
        return True
    except Exception as e:
        logger.error(f"Error saving result to database: {str(e)}")
        return False

def consume_messages(redis_client: redis.Redis) -> None:
    """Consume messages from the Redis stream."""
    try:
        # Read new messages
        messages = redis_client.xreadgroup(
            groupname=REDIS_CONSUMER_GROUP,
            consumername=REDIS_CONSUMER_NAME,
            streams={REDIS_STREAM_NAME: '>'},  # '>' means read new messages
            count=1,  # Process one message at a time
            block=5000  # Block for 5 seconds if no messages
        )

        if not messages:
            logger.debug("No new messages")
            return

        # Process each message
        for stream_name, stream_messages in messages:
            for message_id, message_data in stream_messages:
                logger.info(f"Processing message {message_id}")

                # Process the article
                result = process_article(message_data)

                # Save the result
                if "error" not in result:
                    save_result_to_database(result)

                # Acknowledge the message
                redis_client.xack(REDIS_STREAM_NAME, REDIS_CONSUMER_GROUP, message_id)
                logger.info(f"Acknowledged message {message_id}")
    except Exception as e:
        logger.error(f"Error consuming messages: {str(e)}")

def main():
    """Main function to consume articles from Redis stream."""
    logger.info("Starting Redis consumer")

    try:
        # Connect to Redis
        redis_client = connect_to_redis()

        # Set up the consumer group
        setup_consumer_group(redis_client)

        # Main processing loop
        logger.info(f"Listening for messages on stream '{REDIS_STREAM_NAME}'")
        while True:
            consume_messages(redis_client)
            time.sleep(1)  # Small delay to avoid tight loop
    except KeyboardInterrupt:
        logger.info("Consumer stopped by user")
    except Exception as e:
        logger.error(f"Error in Redis consumer: {str(e)}")

    logger.info("Redis consumer completed")

if __name__ == "__main__":
    main()
