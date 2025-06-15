"""
Scheduled retraining pipeline using a simple approach.
"""
import os
import sys
import time
import logging
import threading
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mlops.train_model import train_and_log_model
from mlops.drift_detection import detect_drift
from mlops.config import RETRAINING_SCHEDULE

# Ensure log directory exists
log_dir = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(log_dir, exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, 'retraining.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def check_for_drift():
    """Check if concept drift has been detected."""
    logger.info("Checking for concept drift...")
    drift_result = detect_drift()
    
    if drift_result is None:
        logger.warning("Could not perform drift detection. Data files not found.")
        return False
    
    if drift_result.get("drift_detected", False):
        logger.info("Concept drift detected:")
        for reason in drift_result.get("drift_reasons", []):
            logger.info(f"- {reason}")
        
        # Log drift metrics
        drift_metrics = drift_result.get("metrics", {})
        if "data_drift" in drift_metrics:
            logger.info(f"Data drift score: {drift_metrics['data_drift']['drift_score']:.3f}")
            if "drifted_features" in drift_metrics["data_drift"]:
                logger.info(f"Number of drifted features: {len(drift_metrics['data_drift']['drifted_features'])}")
        
        if "prediction_drift" in drift_metrics:
            logger.info(f"Prediction drift: {drift_metrics['prediction_drift']:.3f}")
        if "confidence_drift" in drift_metrics:
            logger.info(f"Confidence drift: {drift_metrics['confidence_drift']:.3f}")
            
        logger.info("Drift report saved to: " + drift_result["report_path"])
        return True
        
    logger.info("No significant drift detected.")
    return False

def retrain_model(force_retrain=False, include_feedback=True):
    """Retrain the model if drift is detected or forced."""
    try:
        if force_retrain:
            logger.info("Forced retraining initiated.")
            run_id, metrics = train_and_log_model(include_feedback=include_feedback)
            if run_id:
                logger.info(f"Model retrained successfully. MLflow run ID: {run_id}")
                if metrics:
                    logger.info("Training metrics:")
                    for metric_name, value in metrics.items():
                        logger.info(f"- {metric_name}: {value:.3f}")
            return run_id, metrics
        return None, None
    except Exception as e:
        logger.error(f"Error during model retraining: {str(e)}")
        return None, None

def retraining_flow(force_retrain=False):
    """
    Flow for checking drift and retraining the model if necessary.
    
    Args:
        force_retrain: If True, retrain regardless of drift detection.
    
    Returns:
        dict: Results of the retraining flow including:
            - drift_detected (bool): Whether drift was detected
            - retrained (bool): Whether model was retrained
            - run_id (str): MLflow run ID if retrained, None otherwise
            - metrics (dict): Training metrics if retrained, None otherwise
    """
    result = {
        "drift_detected": False,
        "retrained": False,
        "run_id": None,
        "metrics": None,
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        # Check for drift unless force_retrain is True
        if not force_retrain:
            result["drift_detected"] = check_for_drift()
        
        # Retrain if drift detected or forced
        if result["drift_detected"] or force_retrain:
            run_id, metrics = retrain_model(force_retrain=True, include_feedback=True)
            result["retrained"] = run_id is not None
            result["run_id"] = run_id
            result["metrics"] = metrics
    except Exception as e:
        logger.error(f"Error in retraining flow: {str(e)}")
    
    return result

def run_scheduler():
    """Run the scheduler indefinitely."""
    logger.info("Starting retraining scheduler...")
    
    def run_scheduled_job():
        logger.info("Running scheduled retraining check...")
        result = retraining_flow()
        if result["retrained"]:
            logger.info("Scheduled retraining completed successfully.")
            logger.info(f"MLflow run ID: {result['run_id']}")
        else:
            logger.info("No retraining needed.")
    
    schedule = RETRAINING_SCHEDULE
    logger.info(f"Scheduler started. Will run at {schedule}")
    
    while True:
        # Check current time
        now = datetime.now()
        scheduled_time = datetime.strptime(schedule, "%H:%M").time()
        current_time = now.time()
        
        if current_time.hour == scheduled_time.hour and current_time.minute == scheduled_time.minute:
            run_scheduled_job()
            # Sleep for 60 seconds to avoid running multiple times in the same minute
            time.sleep(60)
        else:
            # Sleep for 30 seconds before checking again
            time.sleep(30)

def start_scheduler():
    """Start the scheduler in a separate thread."""
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    return scheduler_thread

if __name__ == "__main__":
    # Run the scheduler
    scheduler_thread = start_scheduler()
    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user.")
        sys.exit(0)
