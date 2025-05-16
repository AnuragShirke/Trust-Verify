"""
Integration module for connecting the API with MLOps components.
"""
import os
import sys
import joblib
from typing import Dict, Any, Tuple, Optional

# Add project root to path to import MLOps modules
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

# Check if MLOps should be enabled via environment variable
USE_MLFLOW = os.environ.get("USE_MLFLOW", "false").lower() == "true"

try:
    from mlops.mlflow_utils import load_production_model, load_production_vectorizer
    from mlops.feedback_collector import FeedbackCollector
    from mlops.drift_detection import detect_drift

    # Set MLflow tracking URI from environment variable if available
    mlflow_tracking_uri = os.environ.get("MLFLOW_TRACKING_URI")
    if mlflow_tracking_uri:
        import mlflow
        mlflow.set_tracking_uri(mlflow_tracking_uri)
        print(f"MLflow tracking URI set to: {mlflow_tracking_uri}")

    # Only set MLOPS_AVAILABLE to True if both the imports work AND USE_MLFLOW is true
    MLOPS_AVAILABLE = USE_MLFLOW
    if MLOPS_AVAILABLE:
        print("MLOps integration is enabled")
    else:
        print("MLOps integration is disabled via environment variable")
except ImportError:
    MLOPS_AVAILABLE = False
    print("Warning: MLOps modules not available. Using fallback model loading.")

def load_models() -> Tuple[Any, Any, bool]:
    """
    Load the model and vectorizer, trying MLflow first, then local files.

    Returns:
        Tuple containing (vectorizer, classifier, success_flag)
    """
    vectorizer = None
    classifier = None
    models_loaded = False

    # Try to load from MLflow if available
    if MLOPS_AVAILABLE:
        try:
            print("Attempting to load models from MLflow...")

            # Get model name and stage from environment variables
            model_name = os.environ.get("MODEL_NAME", "fake-news-classifier")
            model_stage = os.environ.get("MODEL_STAGE", "Production")
            print(f"Using model: {model_name}, stage: {model_stage}")

            # Load model and vectorizer
            classifier = load_production_model(model_name=model_name, stage=model_stage)
            vectorizer = load_production_vectorizer(model_name=model_name, stage=model_stage)

            if classifier is not None and vectorizer is not None:
                models_loaded = True
                print("Models loaded from MLflow")
                return vectorizer, classifier, models_loaded
        except Exception as e:
            print(f"Warning: Could not load models from MLflow: {e}")

    # Fall back to loading from files
    try:
        # Try to load from parent directory first
        vectorizer = joblib.load(os.path.join(parent_dir, "model", "tfidf_vectorizer.pkl"))
        classifier = joblib.load(os.path.join(parent_dir, "model", "classifier.pkl"))
        models_loaded = True
        print("Models loaded from parent directory")
    except Exception as e:
        print(f"Warning: Could not load models from parent directory: {e}")

        # Try to load from local directory
        try:
            vectorizer = joblib.load(os.path.join("model", "tfidf_vectorizer.pkl"))
            classifier = joblib.load(os.path.join("model", "classifier.pkl"))
            models_loaded = True
            print("Models loaded from local directory")
        except Exception as e:
            print(f"Warning: Could not load models from local directory: {e}")
            models_loaded = False

    return vectorizer, classifier, models_loaded

def submit_feedback(text: str, predicted_label: int, corrected_label: int, source: str = "api") -> bool:
    """
    Submit feedback for a misclassified article.

    Args:
        text: The article text
        predicted_label: The label predicted by the model (0=FAKE, 1=REAL)
        corrected_label: The corrected label provided by the user
        source: Source of the feedback

    Returns:
        bool: True if feedback was saved successfully
    """
    if not MLOPS_AVAILABLE:
        print("Warning: MLOps modules not available. Feedback not saved.")
        return False

    try:
        collector = FeedbackCollector()
        success = collector.submit_feedback(text, predicted_label, corrected_label, source)
        return success
    except Exception as e:
        print(f"Error submitting feedback: {e}")
        return False

def check_drift() -> Dict[str, Any]:
    """
    Check for concept drift in the model.

    Returns:
        Dict containing drift detection results
    """
    if not MLOPS_AVAILABLE:
        print("Warning: MLOps modules not available. Drift detection not performed.")
        return {"drift_detected": False, "error": "MLOps modules not available"}

    try:
        result = detect_drift()
        return result
    except Exception as e:
        print(f"Error checking drift: {e}")
        return {"drift_detected": False, "error": str(e)}

def get_model_info() -> Dict[str, Any]:
    """
    Get information about the currently loaded model.

    Returns:
        Dict containing model information
    """
    if not MLOPS_AVAILABLE:
        return {
            "source": "local",
            "mlops_available": False,
            "version": "unknown"
        }

    try:
        from mlops.mlflow_utils import get_latest_model_version

        # Get model name and stage from environment variables
        model_name = os.environ.get("MODEL_NAME", "fake-news-classifier")
        model_stage = os.environ.get("MODEL_STAGE", "Production")

        model_version = get_latest_model_version(model_name=model_name, stage=model_stage)

        if model_version:
            return {
                "source": "mlflow",
                "mlops_available": True,
                "version": model_version.version,
                "run_id": model_version.run_id,
                "creation_timestamp": model_version.creation_timestamp,
                "last_updated_timestamp": model_version.last_updated_timestamp,
                "current_stage": model_version.current_stage,
                "description": model_version.description,
                "model_name": model_name,
                "model_stage": model_stage
            }
        else:
            return {
                "source": "local",
                "mlops_available": True,
                "version": "unknown"
            }
    except Exception as e:
        print(f"Error getting model info: {e}")
        return {
            "source": "local",
            "mlops_available": True,
            "version": "unknown",
            "error": str(e)
        }
