#!/usr/bin/env python
"""
Scheduler Script

This script schedules the news collector and producer to run at regular intervals.
"""

import os
import time
import logging
import datetime
import subprocess
import schedule
from typing import List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("pipeline/scheduler.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("scheduler")

# Configuration
COLLECTOR_INTERVAL_MINUTES = int(os.environ.get("COLLECTOR_INTERVAL_MINUTES", 30))
PRODUCER_INTERVAL_MINUTES = int(os.environ.get("PRODUCER_INTERVAL_MINUTES", 5))

def run_script(script_path: str) -> bool:
    """Run a Python script as a subprocess."""
    try:
        logger.info(f"Running script: {script_path}")
        
        # Get the Python executable from the current environment
        python_executable = "python"
        
        # Run the script
        process = subprocess.Popen(
            [python_executable, script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait for the process to complete
        stdout, stderr = process.communicate()
        
        # Check if the process was successful
        if process.returncode == 0:
            logger.info(f"Script {script_path} completed successfully")
            return True
        else:
            logger.error(f"Script {script_path} failed with return code {process.returncode}")
            logger.error(f"STDERR: {stderr}")
            return False
    except Exception as e:
        logger.error(f"Error running script {script_path}: {str(e)}")
        return False

def run_news_collector():
    """Run the news collector script."""
    script_path = "pipeline/news_collector.py"
    return run_script(script_path)

def run_redis_producer():
    """Run the Redis producer script."""
    script_path = "pipeline/redis_producer.py"
    return run_script(script_path)

def setup_schedules():
    """Set up the schedules for the collector and producer."""
    # Schedule the news collector
    schedule.every(COLLECTOR_INTERVAL_MINUTES).minutes.do(run_news_collector)
    logger.info(f"Scheduled news collector to run every {COLLECTOR_INTERVAL_MINUTES} minutes")
    
    # Schedule the Redis producer
    schedule.every(PRODUCER_INTERVAL_MINUTES).minutes.do(run_redis_producer)
    logger.info(f"Scheduled Redis producer to run every {PRODUCER_INTERVAL_MINUTES} minutes")

def main():
    """Main function to run the scheduler."""
    logger.info("Starting scheduler")
    
    try:
        # Set up the schedules
        setup_schedules()
        
        # Run the collector and producer once at startup
        run_news_collector()
        time.sleep(5)  # Wait for the collector to finish
        run_redis_producer()
        
        # Main loop to run the scheduled jobs
        logger.info("Entering main scheduler loop")
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")
    except Exception as e:
        logger.error(f"Error in scheduler: {str(e)}")
    
    logger.info("Scheduler completed")

if __name__ == "__main__":
    main()
