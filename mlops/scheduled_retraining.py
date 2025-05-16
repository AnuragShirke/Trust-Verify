"""
Scheduled retraining pipeline using a simple approach.
"""
import os
import sys
import time
import logging
import threading
import schedule
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mlops.train_model import train_and_log_model
from mlops.drift_detection import detect_drift
from mlops.config import RETRAINING_SCHEDULE

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(__file__), 'logs', 'retraining.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def check_for_drift():
    """Check if concept drift has been detected."""
    logger.info("Checking for concept drift...")
    drift_result = detect_drift()
    if drift_result and drift_result.get("drift_detected", False):
        logger.info("Concept drift detected. Triggering model retraining.")
        return True
    logger.info("No significant drift detected.")
    return False

def retrain_model(force_retrain=False, include_feedback=True):
    """Retrain the model if drift is detected or forced."""
    if force_retrain:
        logger.info("Forced retraining initiated.")
        run_id, metrics = train_and_log_model(include_feedback=include_feedback)
        return run_id, metrics
    return None, None

def retraining_flow(force_retrain=False):
    """
    Flow for checking drift and retraining the model if necessary.

    Args:
        force_retrain: If True, retrain regardless of drift detection

    Returns:
        bool: True if retraining was performed, False otherwise
    """
    logger.info("Starting retraining flow")

    # Check for drift if not forcing retraining
    drift_detected = False
    if not force_retrain:
        drift_detected = check_for_drift()

    # Retrain if drift detected or forced
    if drift_detected or force_retrain:
        run_id, metrics = retrain_model(force_retrain=True, include_feedback=True)
        if run_id:
            logger.info(f"Model retrained successfully. Run ID: {run_id}")
            logger.info("Metrics:")
            for key, value in metrics.items():
                logger.info(f"  {key}: {value:.4f}")
            return True
        else:
            logger.error("Model retraining failed.")
            return False

    logger.info("No retraining needed.")
    return False

def run_scheduler():
    """Run the scheduler in a separate thread."""
    stop_event = threading.Event()

    def job():
        logger.info(f"Running scheduled retraining at {datetime.now()}")
        retraining_flow(force_retrain=False)

    # Parse the cron schedule and convert to schedule format
    # For simplicity, we'll just schedule it to run daily at midnight
    schedule.every().day.at("00:00").do(job)

    logger.info(f"Scheduler started. Will run at 00:00 daily.")

    while not stop_event.is_set():
        schedule.run_pending()
        time.sleep(60)  # Check every minute

    logger.info("Scheduler stopped.")

def create_deployment():
    """Create a scheduled retraining job."""
    # Create logs directory if it doesn't exist
    os.makedirs(os.path.join(os.path.dirname(__file__), 'logs'), exist_ok=True)

    # Start the scheduler in a background thread
    scheduler_thread = threading.Thread(target=run_scheduler)
    scheduler_thread.daemon = True
    scheduler_thread.start()

    logger.info("Retraining scheduler started in background thread.")
    return scheduler_thread

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Fake News Detector Model Retraining")
    parser.add_argument("--force", action="store_true", help="Force model retraining")
    parser.add_argument("--deploy", action="store_true", help="Create a scheduled deployment")
    parser.add_argument("--run-once", action="store_true", help="Run the retraining flow once and exit")

    args = parser.parse_args()

    # Create logs directory if it doesn't exist
    os.makedirs(os.path.join(os.path.dirname(__file__), 'logs'), exist_ok=True)

    if args.deploy:
        # Start the scheduler in a background thread
        scheduler_thread = create_deployment()

        try:
            # Keep the main thread alive
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user.")
            sys.exit(0)
    elif args.run_once:
        # Run the retraining flow once
        retraining_flow(force_retrain=False)
    else:
        # Run with force flag
        retraining_flow(force_retrain=args.force)
