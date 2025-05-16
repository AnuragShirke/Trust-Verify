"""
Utility functions for MLflow tracking and model management.
"""
import os
import mlflow
import hashlib
import pandas as pd
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from mlops.config import (
    MLFLOW_TRACKING_URI,
    MLFLOW_EXPERIMENT_NAME,
    MODEL_NAME,
    MODEL_STAGE,
    METRICS
)

def setup_mlflow():
    """Set up MLflow tracking."""
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    experiment = mlflow.get_experiment_by_name(MLFLOW_EXPERIMENT_NAME)
    if experiment is None:
        mlflow.create_experiment(MLFLOW_EXPERIMENT_NAME)
    mlflow.set_experiment(MLFLOW_EXPERIMENT_NAME)
    return mlflow.get_experiment_by_name(MLFLOW_EXPERIMENT_NAME)

def calculate_dataset_hash(df):
    """Calculate a hash of the dataset to track dataset versions."""
    return hashlib.md5(pd.util.hash_pandas_object(df).values).hexdigest()

def log_model_metrics(y_true, y_pred, y_prob=None):
    """Calculate and log model metrics."""
    metrics = {}

    # Basic classification metrics
    metrics["accuracy"] = accuracy_score(y_true, y_pred)
    metrics["precision"] = precision_score(y_true, y_pred, average='weighted')
    metrics["recall"] = recall_score(y_true, y_pred, average='weighted')
    metrics["f1"] = f1_score(y_true, y_pred, average='weighted')

    # ROC AUC if probability scores are available
    if y_prob is not None:
        metrics["roc_auc"] = roc_auc_score(y_true, y_prob)

    return metrics

def log_model_with_mlflow(model, vectorizer, metrics, params, dataset_hash, tags=None):
    """Log model, parameters, metrics, and artifacts with MLflow."""
    with mlflow.start_run():
        # Log parameters
        for key, value in params.items():
            mlflow.log_param(key, value)

        # Log metrics
        for key, value in metrics.items():
            mlflow.log_metric(key, value)

        # Log dataset hash
        mlflow.log_param("dataset_hash", dataset_hash)

        # Log tags
        if tags:
            for key, value in tags.items():
                mlflow.set_tag(key, value)

        # Log model and vectorizer as artifacts
        mlflow.sklearn.log_model(
            model,
            "model",
            registered_model_name=MODEL_NAME
        )

        # Log vectorizer as a pickle artifact
        mlflow.sklearn.log_model(
            vectorizer,
            "vectorizer"
        )

        # Return the run ID
        return mlflow.active_run().info.run_id

def get_latest_model_version(model_name=None, stage=None):
    """
    Get the latest version of the registered model.

    Args:
        model_name: Name of the model (defaults to MODEL_NAME from config)
        stage: Stage of the model (defaults to MODEL_STAGE from config)

    Returns:
        The latest model version object
    """
    client = mlflow.tracking.MlflowClient()
    try:
        # Use provided values or defaults from config
        model_name = model_name or MODEL_NAME
        stage = stage or MODEL_STAGE

        latest_version = client.get_latest_versions(model_name, stages=[stage])
        if latest_version:
            return latest_version[0]
        return None
    except Exception as e:
        print(f"Error getting latest model version: {e}")
        return None

def load_production_model(model_name=None, stage=None):
    """
    Load the production model from MLflow model registry.

    Args:
        model_name: Name of the model (defaults to MODEL_NAME from config)
        stage: Stage of the model (defaults to MODEL_STAGE from config)

    Returns:
        The loaded model
    """
    try:
        # Use provided values or defaults from config
        model_name = model_name or MODEL_NAME
        stage = stage or MODEL_STAGE

        model_uri = f"models:/{model_name}/{stage}"
        print(f"Loading model from: {model_uri}")
        model = mlflow.sklearn.load_model(model_uri)
        return model
    except Exception as e:
        print(f"Error loading production model: {e}")
        return None

def load_production_vectorizer(model_name=None, stage=None):
    """
    Load the production vectorizer from MLflow model registry.

    Args:
        model_name: Name of the model (defaults to MODEL_NAME from config)
        stage: Stage of the model (defaults to MODEL_STAGE from config)

    Returns:
        The loaded vectorizer
    """
    try:
        # Use provided values or defaults from config
        model_name = model_name or MODEL_NAME
        stage = stage or MODEL_STAGE

        client = mlflow.tracking.MlflowClient()
        latest_version = client.get_latest_versions(model_name, stages=[stage])
        if not latest_version:
            print(f"No model version found for {model_name} in stage {stage}")
            return None

        run_id = latest_version[0].run_id
        vectorizer_uri = f"runs:/{run_id}/vectorizer"
        print(f"Loading vectorizer from: {vectorizer_uri}")
        vectorizer = mlflow.sklearn.load_model(vectorizer_uri)
        return vectorizer
    except Exception as e:
        print(f"Error loading production vectorizer: {e}")
        return None

def transition_model_to_production(run_id):
    """Transition a model version to production stage."""
    client = mlflow.tracking.MlflowClient()

    # Get the model version
    model_versions = client.get_latest_versions(MODEL_NAME)
    for model_version in model_versions:
        if model_version.run_id == run_id:
            version = model_version.version
            # Transition the model to production
            client.transition_model_version_stage(
                name=MODEL_NAME,
                version=version,
                stage=MODEL_STAGE
            )
            print(f"Model version {version} transitioned to {MODEL_STAGE}")
            return True

    print(f"No model version found for run_id {run_id}")
    return False
