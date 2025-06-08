#!/usr/bin/env python
"""
Start Script

This script ensures proper initialization of the pipeline services.
"""

import os
import sys
import time
import logging
import subprocess
from typing import List, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("start_script")

def run_deployment_check() -> bool:
    """Run deployment checks."""
    try:
        result = subprocess.run([sys.executable, "deployment_check.py"], check=True)
        return result.returncode == 0
    except subprocess.CalledProcessError:
        return False

def start_services() -> List[Tuple[subprocess.Popen, str]]:
    """Start all pipeline services."""
    services = []
    
    try:
        # Start Redis consumer
        consumer = subprocess.Popen(
            [sys.executable, "redis_consumer.py"],
            env=os.environ.copy()
        )
        services.append((consumer, "Redis Consumer"))
        
        # Start news collector
        collector = subprocess.Popen(
            [sys.executable, "news_collector.py"],
            env=os.environ.copy()
        )
        services.append((collector, "News Collector"))
        
        # Start dashboard server
        dashboard = subprocess.Popen(
            [sys.executable, "dashboard_server.py"],
            env=os.environ.copy()
        )
        services.append((dashboard, "Dashboard Server"))
        
        # Start scheduler
        scheduler = subprocess.Popen(
            [sys.executable, "scheduler.py"],
            env=os.environ.copy()
        )
        services.append((scheduler, "Scheduler"))
        
        return services
    
    except Exception as e:
        # If any service fails to start, kill all started services
        for process, name in services:
            try:
                process.kill()
                logger.info(f"Killed {name} due to startup error")
            except:
                pass
        raise Exception(f"Failed to start services: {str(e)}")

def main():
    """Main entry point."""
    logger.info("Starting pipeline services...")
    
    # Run deployment checks
    if not run_deployment_check():
        logger.error("Deployment checks failed. Please fix the issues and try again.")
        return 1
    
    try:
        # Start all services
        services = start_services()
        logger.info("All services started successfully!")
        
        # Wait for services
        while True:
            for process, name in services:
                if process.poll() is not None:
                    logger.error(f"{name} exited unexpectedly with code {process.returncode}")
                    # Kill all other services
                    for p, n in services:
                        if p != process:
                            try:
                                p.kill()
                                logger.info(f"Killed {n} due to {name} failure")
                            except:
                                pass
                    return 1
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Received shutdown signal, stopping services...")
        for process, name in services:
            try:
                process.terminate()
                process.wait(timeout=5)
                logger.info(f"Stopped {name}")
            except:
                process.kill()
                logger.info(f"Killed {name}")
        
    return 0

if __name__ == "__main__":
    sys.exit(main())
