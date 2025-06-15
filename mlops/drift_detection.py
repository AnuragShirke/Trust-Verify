"""
Concept drift detection for the fake news detector model.
"""
import os
import pandas as pd
import numpy as np
import json
from datetime import datetime
from scipy import stats
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

def convert_to_serializable(obj):
    """Convert NumPy and other types to JSON-serializable Python types."""
    if isinstance(obj, dict):
        return {k: convert_to_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_serializable(v) for v in obj]
    elif isinstance(obj, (np.floating, float)):
        return float(obj)
    elif isinstance(obj, (np.integer, int)):
        return int(obj)
    elif isinstance(obj, (np.bool_, bool)):
        return bool(obj)
    elif isinstance(obj, str):
        return str(obj)
    elif obj is None:
        return None
    else:
        return str(obj)

def detect_drift_for_feature(reference_values, current_values, threshold=0.05):
    """Detect drift for a single feature using Kolmogorov-Smirnov test."""
    try:
        statistic, p_value = stats.ks_2samp(reference_values, current_values)
        return {
            "drift_detected": p_value < threshold,
            "drift_score": float(p_value),
            "statistic": float(statistic)
        }
    except Exception as e:
        print(f"Warning: Could not calculate drift: {e}")
        return {
            "drift_detected": False,
            "drift_score": 1.0,
            "statistic": 0.0
        }

def extract_text_features(reference_texts=None, current_texts=None, max_features=1000):
    """Extract features from text data for drift detection.
    
    Args:
        reference_texts: Reference text data to fit the vectorizer
        current_texts: Current text data to transform
        max_features: Maximum number of features
    
    Returns:
        Tuple of (reference_features, current_features) DataFrames
    """
    vectorizer = CountVectorizer(max_features=max_features)
    
    # Fit on reference data
    reference_features = vectorizer.fit_transform(reference_texts).toarray()
    feature_names = vectorizer.get_feature_names_out()
    reference_df = pd.DataFrame(reference_features, columns=feature_names)
    
    # Transform current data with the same vocabulary
    if current_texts is not None:
        current_features = vectorizer.transform(current_texts).toarray()
        current_df = pd.DataFrame(current_features, columns=feature_names)
        return reference_df, current_df
    
    return reference_df

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
    
    # Calculate prediction distribution drift
    ref_pos_rate = np.mean(reference_preds)
    curr_pos_rate = np.mean(current_preds)
    pred_drift = abs(ref_pos_rate - curr_pos_rate)
    
    # Calculate confidence drift using class probabilities
    ref_probs = model.predict_proba(reference_features)
    curr_probs = model.predict_proba(current_features)
    ref_conf = np.mean(np.max(ref_probs, axis=1))
    curr_conf = np.mean(np.max(curr_probs, axis=1))
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
    if not os.path.exists(reference_path):
        print(f"Reference data file not found: {reference_path}")
        return None
    
    if not os.path.exists(current_path):
        print(f"Current data file not found: {current_path}")
        print("Using a subset of reference data as current data for demonstration")
        reference_df = pd.read_csv(reference_path)
        # Split reference data into two parts
        split_idx = len(reference_df) // 2
        current_df = reference_df.iloc[split_idx:]
        reference_df = reference_df.iloc[:split_idx]
    else:
        # Load both datasets normally
        reference_df = pd.read_csv(reference_path)
        current_df = pd.read_csv(current_path)
    
    # Extract features for data drift detection
    reference_features, current_features = extract_text_features(
        reference_texts=reference_df["text"],
        current_texts=current_df["text"]
    )
    
    # Calculate drift for each feature
    drift_metrics = {}
    drift_metrics["data_drift"] = {
        "drift_by_feature": {}
    }
    
    for column in reference_features.columns:
        drift_metrics["data_drift"]["drift_by_feature"][column] = detect_drift_for_feature(
            reference_features[column],
            current_features[column]
        )
    
    # Calculate overall drift score as percentage of features with drift
    drifted_features = [
        feature for feature, metrics in drift_metrics["data_drift"]["drift_by_feature"].items()
        if metrics["drift_detected"]
    ]
    drift_metrics["data_drift"]["drift_score"] = len(drifted_features) / len(reference_features.columns)
    drift_metrics["data_drift"]["drifted_features"] = drifted_features
    
    # Calculate prediction drift if model is available
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
    
    # Convert metrics to JSON-serializable format
    drift_metrics_json = convert_to_serializable(drift_metrics)
    
    with open(report_path, "w") as f:
        json.dump(drift_metrics_json, f, indent=2)
    
    # Check if drift exceeds threshold
    drift_detected = False
    drift_reasons = []
    
    if "data_drift" in drift_metrics and drift_metrics["data_drift"]["drift_score"] > DRIFT_THRESHOLD:
        drift_detected = True
        drift_reasons.append(f"Data drift score {drift_metrics['data_drift']['drift_score']:.3f} exceeds threshold {DRIFT_THRESHOLD}")
    
    if pred_drift is not None and pred_drift > DRIFT_THRESHOLD:
        drift_detected = True
        drift_reasons.append(f"Prediction drift {pred_drift:.3f} exceeds threshold {DRIFT_THRESHOLD}")
    
    if conf_drift is not None and conf_drift > DRIFT_THRESHOLD:
        drift_detected = True
        drift_reasons.append(f"Confidence drift {conf_drift:.3f} exceeds threshold {DRIFT_THRESHOLD}")
    
    result = {
        "drift_detected": drift_detected,
        "metrics": drift_metrics_json,
        "report_path": report_path
    }
    
    if drift_detected:
        result["drift_reasons"] = drift_reasons
        print("\nDrift detected for the following reasons:")
        for reason in drift_reasons:
            print(f"- {reason}")
    
    return result

if __name__ == "__main__":
    # Run drift detection
    result = detect_drift()
    if result:
        print(f"Drift detected: {result['drift_detected']}")
        if result['drift_detected']:
            print("Concept drift detected! Consider retraining the model.")
        print(f"Drift report saved to: {result['report_path']}")
