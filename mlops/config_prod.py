"""MLOps Configuration for production deployment."""
import os

# MLflow configuration
MLFLOW_TRACKING_URI = os.environ.get("MLFLOW_TRACKING_URI", "http://localhost:5000")
MLFLOW_EXPERIMENT_NAME = "fake_news_detector"

# Model paths
MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "model")
VECTORIZER_PATH = os.path.join(MODEL_DIR, "tfidf_vectorizer.pkl")
CLASSIFIER_PATH = os.path.join(MODEL_DIR, "classifier.pkl")

# Data paths
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
FEEDBACK_PATH = os.path.join(DATA_DIR, "feedback.csv")

# Redis configuration
REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD", None)

# API configuration
API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")

# Retraining configuration
MIN_FEEDBACK_SAMPLES = 50
RETRAINING_SCHEDULE = os.environ.get("RETRAINING_SCHEDULE", "0 0 * * *")  # Daily at midnight
DRIFT_CHECK_INTERVAL = int(os.environ.get("DRIFT_CHECK_INTERVAL", 24))  # Hours

# Notification configuration
NOTIFICATION_URL = os.environ.get("NOTIFICATION_URL", None)
