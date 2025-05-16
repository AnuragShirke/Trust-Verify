"""
Enhanced model training script with MLflow integration.
"""
import os
import pandas as pd
import numpy as np
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.pipeline import Pipeline
from mlops.config import (
    MODEL_DIR,
    MAX_DF,
    RANDOM_STATE
)
from mlops.data_prep import prepare_data
from mlops.mlflow_utils import (
    setup_mlflow,
    calculate_dataset_hash,
    log_model_metrics,
    log_model_with_mlflow,
    transition_model_to_production
)

def train_model(X_train, y_train, params=None):
    """Train a fake news detection model with the given parameters."""
    if params is None:
        params = {
            "max_df": MAX_DF,
            "random_state": RANDOM_STATE,
            "C": 1.0,
            "solver": "liblinear",
            "max_iter": 100
        }
    
    # Create TF-IDF vectorizer
    tfidf = TfidfVectorizer(
        stop_words="english", 
        max_df=params["max_df"]
    )
    
    # Create classifier
    clf = LogisticRegression(
        C=params["C"],
        solver=params["solver"],
        max_iter=params["max_iter"],
        random_state=params["random_state"]
    )
    
    # Transform training data
    X_train_tfidf = tfidf.fit_transform(X_train)
    
    # Train model
    clf.fit(X_train_tfidf, y_train)
    
    return clf, tfidf

def evaluate_model(clf, tfidf, X_test, y_test):
    """Evaluate the trained model on test data."""
    # Transform test data
    X_test_tfidf = tfidf.transform(X_test)
    
    # Make predictions
    y_pred = clf.predict(X_test_tfidf)
    y_prob = clf.predict_proba(X_test_tfidf)[:, 1]
    
    # Calculate metrics
    metrics = log_model_metrics(y_test, y_pred, y_prob)
    
    # Print classification report
    print(classification_report(y_test, y_pred))
    
    return metrics, y_pred, y_prob

def save_model_locally(clf, tfidf):
    """Save the model and vectorizer locally."""
    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(tfidf, os.path.join(MODEL_DIR, "tfidf_vectorizer.pkl"))
    joblib.dump(clf, os.path.join(MODEL_DIR, "classifier.pkl"))
    print(f"Model and vectorizer saved to {MODEL_DIR}")

def train_and_log_model(params=None, include_feedback=True, save_local=True):
    """Train a model, evaluate it, and log it with MLflow."""
    # Set up MLflow
    experiment = setup_mlflow()
    print(f"MLflow experiment: {experiment.name} (ID: {experiment.experiment_id})")
    
    # Prepare data
    X_train, X_test, y_train, y_test = prepare_data(include_feedback=include_feedback)
    if X_train is None:
        print("Failed to prepare data. Exiting.")
        return None
    
    # Calculate dataset hash
    train_df = pd.DataFrame({"text": X_train, "label": y_train})
    dataset_hash = calculate_dataset_hash(train_df)
    print(f"Dataset hash: {dataset_hash}")
    
    # Train model
    clf, tfidf = train_model(X_train, y_train, params)
    
    # Evaluate model
    metrics, y_pred, y_prob = evaluate_model(clf, tfidf, X_test, y_test)
    print("Model evaluation metrics:")
    for key, value in metrics.items():
        print(f"  {key}: {value:.4f}")
    
    # Log model with MLflow
    if params is None:
        params = {
            "max_df": MAX_DF,
            "random_state": RANDOM_STATE,
            "C": 1.0,
            "solver": "liblinear",
            "max_iter": 100
        }
    
    tags = {
        "include_feedback": str(include_feedback),
        "model_type": "LogisticRegression",
        "vectorizer": "TfidfVectorizer"
    }
    
    run_id = log_model_with_mlflow(clf, tfidf, metrics, params, dataset_hash, tags)
    print(f"Model logged with MLflow (Run ID: {run_id})")
    
    # Transition model to production
    transition_model_to_production(run_id)
    
    # Save model locally if requested
    if save_local:
        save_model_locally(clf, tfidf)
    
    return run_id, metrics

if __name__ == "__main__":
    # Train and log model with default parameters
    run_id, metrics = train_and_log_model()
    print(f"Training completed. Run ID: {run_id}")
