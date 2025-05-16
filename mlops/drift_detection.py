"""
Concept drift detection for the fake news detector model.
"""
import os
import pandas as pd
import numpy as np
import json
from datetime import datetime
from evidently.report import Report
from evidently.metrics import DataDriftTable
from evidently.metrics.base_metric import generate_column_metrics
from sklearn.feature_extraction.text import CountVectorizer
from mlops.config import (
    MLOPS_DIR,
    PROCESSED_DATA_DIR,
    DRIFT_THRESHOLD
)
from mlops.mlflow_utils import (
    load_production_model,
    load_production_vectorizer
)

# Directory to store drift detection results
DRIFT_DIR = os.path.join(MLOPS_DIR, "drift")
os.makedirs(DRIFT_DIR, exist_ok=True)

def extract_text_features(texts, max_features=1000):
    """Extract features from text data for drift detection."""
    vectorizer = CountVectorizer(max_features=max_features)
    features = vectorizer.fit_transform(texts).toarray()
    feature_names = vectorizer.get_feature_names_out()
    
    # Convert to DataFrame for Evidently
    df = pd.DataFrame(features, columns=feature_names)
    return df

def calculate_prediction_drift(model, vectorizer, reference_data, current_data):
    """Calculate drift in model predictions between reference and current data."""
    if model is None or vectorizer is None:
        print("Model or vectorizer not available")
        return None, None
    
    # Transform data
    reference_features = vectorizer.transform(reference_data)
    current_features = vectorizer.transform(current_data)
    
    # Get predictions and probabilities
    reference_preds = model.predict(reference_features)
    current_preds = model.predict(current_features)
    
    reference_probs = model.predict_proba(reference_features)[:, 1]
    current_probs = model.predict_proba(current_features)[:, 1]
    
    # Calculate prediction distribution drift
    ref_pos_rate = np.mean(reference_preds)
    curr_pos_rate = np.mean(current_preds)
    
    pred_drift = abs(ref_pos_rate - curr_pos_rate)
    
    # Calculate confidence drift
    ref_conf = np.mean(np.max(model.predict_proba(reference_features), axis=1))
    curr_conf = np.mean(np.max(model.predict_proba(current_features), axis=1))
    
    conf_drift = abs(ref_conf - curr_conf)
    
    return pred_drift, conf_drift

def detect_drift(reference_path=None, current_path=None):
    """
    Detect concept drift between reference and current datasets.
    
    If paths are not provided, uses the train dataset as reference
    and test dataset as current.
    """
    # Set default paths if not provided
    if reference_path is None:
        reference_path = os.path.join(PROCESSED_DATA_DIR, "train.csv")
    if current_path is None:
        current_path = os.path.join(PROCESSED_DATA_DIR, "test.csv")
    
    # Check if files exist
    if not os.path.exists(reference_path) or not os.path.exists(current_path):
        print(f"Reference or current data file not found")
        return None
    
    # Load data
    reference_df = pd.read_csv(reference_path)
    current_df = pd.read_csv(current_path)
    
    # Extract features for data drift detection
    reference_features = extract_text_features(reference_df["text"])
    current_features = extract_text_features(current_df["text"])
    
    # Create Evidently report for data drift
    data_drift_report = Report(metrics=[DataDriftTable()])
    data_drift_report.run(reference_data=reference_features, current_data=current_features)
    
    # Extract drift metrics
    drift_metrics = {}
    for metric in data_drift_report.metrics:
        drift_metrics.update(metric.get_result())
    
    # Calculate prediction drift
    model = load_production_model()
    vectorizer = load_production_vectorizer()
    
    pred_drift, conf_drift = calculate_prediction_drift(
        model, vectorizer, reference_df["text"], current_df["text"]
    )
    
    # Add prediction drift to metrics
    if pred_drift is not None and conf_drift is not None:
        drift_metrics["prediction_drift"] = pred_drift
        drift_metrics["confidence_drift"] = conf_drift
    
    # Save drift report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = os.path.join(DRIFT_DIR, f"drift_report_{timestamp}.json")
    
    with open(report_path, "w") as f:
        json.dump(drift_metrics, f, indent=2)
    
    # Check if drift exceeds threshold
    drift_detected = False
    if "data_drift" in drift_metrics and drift_metrics["data_drift"]["drift_score"] > DRIFT_THRESHOLD:
        drift_detected = True
    
    if pred_drift is not None and pred_drift > DRIFT_THRESHOLD:
        drift_detected = True
    
    if conf_drift is not None and conf_drift > DRIFT_THRESHOLD:
        drift_detected = True
    
    return {
        "drift_detected": drift_detected,
        "metrics": drift_metrics,
        "report_path": report_path
    }

if __name__ == "__main__":
    # Run drift detection
    result = detect_drift()
    if result:
        print(f"Drift detected: {result['drift_detected']}")
        if result['drift_detected']:
            print("Concept drift detected! Consider retraining the model.")
        print(f"Drift report saved to: {result['report_path']}")
