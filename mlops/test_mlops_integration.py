import requests
import json
import logging
import os
import sys
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_mlops_integration():
    """Test MLOps integration with the main API"""
    
    # Test article to verify prediction and drift detection
    test_article = {
        "title": "Breaking News: Important Discovery",
        "text": "Scientists have made a groundbreaking discovery in the field of renewable energy.",
        "url": "https://example.com/test-article"
    }

    try:
        # 1. Test API Prediction
        api_url = os.environ.get("API_URL", "http://localhost:8000")
        response = requests.post(f"{api_url}/predict", json=test_article)
        
        if response.status_code == 200:
            logger.info("✅ API Prediction Test: Successful")
            logger.info(f"Prediction Response: {response.json()}")
        else:
            logger.error(f"❌ API Prediction Test Failed: {response.status_code}")
            logger.error(response.text)

        # 2. Test Feedback Submission
        feedback_data = {
            "article_url": test_article["url"],
            "prediction": "real",
            "actual_label": "real",
            "feedback_source": "test",
            "timestamp": datetime.now().isoformat()
        }
        
        response = requests.post(f"{api_url}/submit-feedback", json=feedback_data)
        
        if response.status_code == 200:
            logger.info("✅ Feedback Submission Test: Successful")
        else:
            logger.error(f"❌ Feedback Submission Test Failed: {response.status_code}")
            logger.error(response.text)

        # 3. Check MLflow Connection
        mlflow_url = os.environ.get("MLFLOW_TRACKING_URI")
        if mlflow_url:
            response = requests.get(mlflow_url)
            if response.status_code == 200:
                logger.info("✅ MLflow Connection Test: Successful")
            else:
                logger.error(f"❌ MLflow Connection Test Failed: {response.status_code}")
        else:
            logger.warning("⚠️ MLflow URL not configured")

    except Exception as e:
        logger.error(f"❌ Test Failed with error: {str(e)}")

if __name__ == "__main__":
    test_mlops_integration()
