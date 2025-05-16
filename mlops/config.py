"""
Configuration settings for MLOps components.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = os.path.join(BASE_DIR, "data")
MODEL_DIR = os.path.join(BASE_DIR, "model")
MLOPS_DIR = os.path.join(BASE_DIR, "mlops")

# MLflow settings
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "sqlite:///mlruns.db")
MLFLOW_EXPERIMENT_NAME = os.getenv("MLFLOW_EXPERIMENT_NAME", "fake-news-detector")
ARTIFACT_LOCATION = os.getenv("ARTIFACT_LOCATION", os.path.join(MLOPS_DIR, "mlruns"))

# Model settings
MODEL_NAME = "fake-news-classifier"
MODEL_STAGE = "Production"

# Dataset paths
RAW_DATA_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, "processed")
FAKE_NEWS_PATH = os.path.join(RAW_DATA_DIR, "Fake.csv")
REAL_NEWS_PATH = os.path.join(RAW_DATA_DIR, "True.csv")

# Training parameters
TEST_SIZE = 0.2
RANDOM_STATE = 42
MAX_DF = 0.7

# Retraining settings
RETRAINING_SCHEDULE = "0 0 * * 0"  # Weekly at midnight on Sunday
DRIFT_THRESHOLD = 0.1  # Threshold for concept drift detection

# Feedback collection
FEEDBACK_PATH = os.path.join(DATA_DIR, "feedback.csv")

# Metrics to track
METRICS = [
    "accuracy",
    "precision",
    "recall",
    "f1",
    "roc_auc",
]

# Create directories if they don't exist
os.makedirs(MLOPS_DIR, exist_ok=True)
os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
