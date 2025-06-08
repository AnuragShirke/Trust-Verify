#!/usr/bin/env python
"""
Deployment Check Script

This script validates the deployment configuration and environment variables.
"""

import os
import sys
import redis
import requests
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    load_dotenv(env_path)
else:
    print("Warning: .env file not found. Make sure environment variables are set.")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("deployment_check")

def check_redis_connection():
    """Check Redis connection and functionality."""
    redis_host = os.environ.get("REDIS_HOST")
    redis_port = os.environ.get("REDIS_PORT")
    redis_password = os.environ.get("REDIS_PASSWORD")
    
    if not all([redis_host, redis_port, redis_password]):
        logger.error("❌ Missing Redis configuration")
        logger.error(f"  - REDIS_HOST: {'✓' if redis_host else '✗'}")
        logger.error(f"  - REDIS_PORT: {'✓' if redis_port else '✗'}")
        logger.error(f"  - REDIS_PASSWORD: {'✓' if redis_password else '✗'}")
        return False
    
    try:
        # Try to connect
        client = redis.Redis(
            host=redis_host,
            port=int(redis_port),
            password=redis_password,
            decode_responses=True,
            socket_timeout=5,
            socket_connect_timeout=5
        )
        
        # Test basic operations
        client.ping()
        logger.info("✅ Redis ping successful")
        
        # Test write operation
        client.set("test_key", "test_value", ex=10)  # Expires in 10 seconds
        logger.info("✅ Redis write successful")
        
        # Test read operation
        test_value = client.get("test_key")
        if test_value == "test_value":
            logger.info("✅ Redis read successful")
        else:
            raise Exception("Redis read value mismatch")
            
        # Clean up test key
        client.delete("test_key")
        
        return True
        
    except redis.ConnectionError as e:
        logger.error(f"❌ Redis connection failed: {str(e)}")
        logger.error(f"  - Check if Redis is running at {redis_host}:{redis_port}")
        return False
    except redis.AuthenticationError:
        logger.error("❌ Redis authentication failed - check password")
        return False
    except redis.TimeoutError:
        logger.error("❌ Redis connection timeout")
        return False
    except Exception as e:
        logger.error(f"❌ Redis operation failed: {str(e)}")
        return False

def check_api_connection():
    """Check API connection and health."""
    api_url = os.environ.get("API_BASE_URL")
    if not api_url:
        logger.error("❌ Missing API_BASE_URL")
        return False
    
    try:
        # Remove trailing slash if present
        api_url = api_url.rstrip('/')
        logger.info(f"Checking API health at: {api_url}/health")
        
        response = requests.get(f"{api_url}/health", timeout=10)
        logger.info(f"API Response Status: {response.status_code}")
        
        # Log raw response for debugging
        try:
            logger.info(f"API Response Body: {response.text[:500]}")  # First 500 chars
        except:
            logger.warning("Could not log response body")
            
        response.raise_for_status()
        
        # Check API health status
        health_data = response.json()
        if health_data.get("status") == "healthy":
            logger.info("✅ API connection successful")
            logger.info(f"✅ API Version: {health_data.get('version', 'unknown')}")
            if health_data.get("models_loaded", False):
                logger.info("✅ API models loaded")
            else:
                logger.warning("⚠️ API models not loaded")
            return True
        else:
            logger.error(f"❌ API unhealthy: {health_data.get('error', 'Unknown error')}")
            return False
            
    except requests.Timeout:
        logger.error("❌ API connection timeout")
        return False
    except requests.ConnectionError:
        logger.error("❌ API connection failed - service may be down")
        return False
    except Exception as e:
        logger.error(f"❌ API connection failed: {str(e)}")
        return False

def main():
    """Run all deployment checks."""
    logger.info("Starting deployment checks...")
    
    redis_ok = check_redis_connection()
    api_ok = check_api_connection()
    
    if redis_ok and api_ok:
        logger.info("✅ All checks passed! Deployment ready.")
        return 0
    else:
        logger.error("❌ Some checks failed. Please fix the issues before deploying.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
