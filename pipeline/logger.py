#!/usr/bin/env python
"""
Logging Configuration Module

This module provides a centralized logging configuration using loguru.
"""

import os
import sys
import json
from datetime import datetime
from loguru import logger

# Create logs directory if it doesn't exist
os.makedirs("pipeline/logs", exist_ok=True)

# Remove default logger
logger.remove()

# Add console logger
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO"
)

# Add file logger for all logs
logger.add(
    "pipeline/logs/pipeline_{time:YYYY-MM-DD}.log",
    rotation="00:00",  # New file at midnight
    retention="30 days",  # Keep logs for 30 days
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="DEBUG"
)

# Add file logger for errors only
logger.add(
    "pipeline/logs/errors_{time:YYYY-MM-DD}.log",
    rotation="00:00",
    retention="30 days",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="ERROR"
)

# Add JSON logger for structured logging
class JsonSink:
    def __init__(self, file_path):
        self.file_path = file_path
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    def write(self, message):
        record = message.record
        log_entry = {
            "timestamp": record["time"].isoformat(),
            "level": record["level"].name,
            "message": record["message"],
            "name": record["name"],
            "function": record["function"],
            "line": record["line"],
            "process": record["process"].id,
            "thread": record["thread"].id,
            "exception": record["exception"],
        }
        
        with open(self.file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")

logger.add(
    JsonSink("pipeline/logs/structured_{time:YYYY-MM-DD}.json"),
    format="{message}",
    level="INFO"
)

# Function to get a logger for a specific module
def get_logger(name):
    """Get a configured logger for a specific module."""
    return logger.bind(name=name)

# Export the logger
__all__ = ["logger", "get_logger"]
