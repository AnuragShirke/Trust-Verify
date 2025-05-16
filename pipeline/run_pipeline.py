#!/usr/bin/env python
"""
Run Pipeline Script

This script runs the entire real-time news pipeline.
"""

import os
import sys
import time
import argparse
import subprocess
from typing import List, Dict, Any

# Import the logger
from logger import get_logger

# Get logger for this module
logger = get_logger("run_pipeline")

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Run the real-time news pipeline")

    parser.add_argument(
        "--collector",
        action="store_true",
        help="Run the news collector"
    )

    parser.add_argument(
        "--producer",
        action="store_true",
        help="Run the Redis producer"
    )

    parser.add_argument(
        "--consumer",
        action="store_true",
        help="Run the Redis consumer"
    )

    parser.add_argument(
        "--dashboard",
        action="store_true",
        help="Run the dashboard server"
    )

    parser.add_argument(
        "--scheduler",
        action="store_true",
        help="Run the scheduler"
    )

    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all components"
    )

    return parser.parse_args()

def run_script(script_path: str, wait: bool = False) -> subprocess.Popen:
    """Run a Python script as a subprocess."""
    try:
        logger.info(f"Running script: {script_path}")

        # Get the Python executable from the current environment
        python_executable = sys.executable

        # Run the script
        process = subprocess.Popen(
            [python_executable, script_path],
            stdout=subprocess.PIPE if not wait else None,
            stderr=subprocess.PIPE if not wait else None,
            text=True
        )

        if wait:
            # Wait for the process to complete
            process.wait()
            logger.info(f"Script {script_path} completed with return code {process.returncode}")
        else:
            logger.info(f"Started script {script_path} with PID {process.pid}")

        return process
    except Exception as e:
        logger.error(f"Error running script {script_path}: {str(e)}")
        return None

def main():
    """Main function to run the pipeline."""
    logger.info("Starting pipeline")

    # Parse arguments
    args = parse_arguments()

    # Determine which components to run
    run_all = args.all
    run_collector = args.collector or run_all
    run_producer = args.producer or run_all
    run_consumer = args.consumer or run_all
    run_dashboard = args.dashboard or run_all
    run_scheduler = args.scheduler or run_all

    # If no specific component is specified, run all
    if not any([run_collector, run_producer, run_consumer, run_dashboard, run_scheduler]):
        run_all = True
        run_collector = run_producer = run_consumer = run_dashboard = run_scheduler = True

    # Keep track of started processes
    processes = []

    try:
        # Run the collector if requested
        if run_collector:
            collector_process = run_script("news_collector.py", wait=True)

        # Run the producer if requested
        if run_producer:
            producer_process = run_script("redis_producer.py", wait=True)

        # Run the consumer if requested
        if run_consumer:
            consumer_process = run_script("redis_consumer.py")
            if consumer_process:
                processes.append(("consumer", consumer_process))

        # Run the dashboard if requested
        if run_dashboard:
            dashboard_process = run_script("dashboard_server.py")
            if dashboard_process:
                processes.append(("dashboard", dashboard_process))

        # Run the scheduler if requested
        if run_scheduler:
            scheduler_process = run_script("scheduler.py")
            if scheduler_process:
                processes.append(("scheduler", scheduler_process))

        # Wait for processes to complete
        logger.info("All requested components started")

        if processes:
            try:
                while True:
                    # Check if any process has terminated
                    for name, process in processes:
                        if process.poll() is not None:
                            logger.warning(f"{name} process terminated with return code {process.returncode}")

                    # Sleep for a bit
                    time.sleep(1)
            except KeyboardInterrupt:
                logger.info("Received keyboard interrupt, shutting down...")

                # Terminate all processes
                for name, process in processes:
                    logger.info(f"Terminating {name} process (PID {process.pid})")
                    process.terminate()

                # Wait for processes to terminate
                for name, process in processes:
                    try:
                        process.wait(timeout=5)
                        logger.info(f"{name} process terminated")
                    except subprocess.TimeoutExpired:
                        logger.warning(f"{name} process did not terminate, killing...")
                        process.kill()
    except Exception as e:
        logger.error(f"Error in pipeline: {str(e)}")

    logger.info("Pipeline completed")

if __name__ == "__main__":
    main()
