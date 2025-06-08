"""
Initialize the MLOps environment.

This script:
1. Sets up the MLflow tracking server
2. Creates the initial experiment
3. Trains and logs the first model
4. Transitions the model to production
"""
import os
import sys
import mlflow
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

# Add the parent directory to the path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from mlops.config import (
    MLFLOW_TRACKING_URI,
    MLFLOW_EXPERIMENT_NAME,
    ARTIFACT_LOCATION,
    MODEL_NAME,
    MODEL_STAGE
)
from mlops.train_model import train_and_log_model

app = FastAPI(title="Trust Verify MLOps Service")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def setup_mlflow_server():
    """Set up and start the MLflow tracking server."""
    print(f"MLflow tracking URI: {MLFLOW_TRACKING_URI}")
    print(f"MLflow experiment name: {MLFLOW_EXPERIMENT_NAME}")
    print(f"MLflow artifact location: {ARTIFACT_LOCATION}")
    
    # Create artifact location directory if it doesn't exist
    os.makedirs(ARTIFACT_LOCATION, exist_ok=True)
    
    # Set tracking URI
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    
    # Create experiment if it doesn't exist
    experiment = mlflow.get_experiment_by_name(MLFLOW_EXPERIMENT_NAME)
    if experiment is None:
        mlflow.create_experiment(
            name=MLFLOW_EXPERIMENT_NAME,
            artifact_location=ARTIFACT_LOCATION
        )
        print(f"Created MLflow experiment: {MLFLOW_EXPERIMENT_NAME}")
    else:
        print(f"Using existing MLflow experiment: {MLFLOW_EXPERIMENT_NAME} (ID: {experiment.experiment_id})")

def train_initial_model():
    """Train and log the initial model."""
    print("Training and logging initial model...")
    run_id, metrics = train_and_log_model(save_local=True)
    
    if run_id:
        print(f"Initial model trained and logged successfully. Run ID: {run_id}")
        print("Metrics:")
        for key, value in metrics.items():
            print(f"  {key}: {value:.4f}")
        return run_id
    else:
        print("Failed to train initial model.")
        return None

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    try:
        # Check MLflow connection
        mlflow.set_tracking_uri(os.environ.get("MLFLOW_TRACKING_URI"))
        mlflow.list_experiments()
        
        return {
            "status": "healthy",
            "mlflow_connected": True,
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

def main():
    """Main function to initialize the MLOps environment."""
    print("Initializing MLOps environment...")
    
    # Set up MLflow server
    setup_mlflow_server()
    
    # Train initial model
    run_id = train_initial_model()
    
    if run_id:
        print("MLOps environment initialized successfully.")
    else:
        print("Failed to initialize MLOps environment.")

if __name__ == "__main__":
    main()
