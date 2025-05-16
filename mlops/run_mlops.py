"""
Main script to run the MLOps pipeline.
"""
import os
import argparse
import mlflow
from mlops.config import (
    MLFLOW_TRACKING_URI,
    MLFLOW_EXPERIMENT_NAME,
    ARTIFACT_LOCATION
)
from mlops.train_model import train_and_log_model
from mlops.drift_detection import detect_drift
from mlops.scheduled_retraining import retraining_flow, create_deployment
from mlops.feedback_collector import FeedbackCollector

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

def main():
    """Main function to run the MLOps pipeline."""
    parser = argparse.ArgumentParser(description="Fake News Detector MLOps Pipeline")
    
    # Add subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Setup command
    setup_parser = subparsers.add_parser("setup", help="Set up the MLOps environment")
    
    # Train command
    train_parser = subparsers.add_parser("train", help="Train and log a model")
    train_parser.add_argument("--no-feedback", action="store_true", help="Don't include feedback data")
    train_parser.add_argument("--no-local-save", action="store_true", help="Don't save model locally")
    
    # Drift command
    drift_parser = subparsers.add_parser("drift", help="Detect concept drift")
    
    # Retrain command
    retrain_parser = subparsers.add_parser("retrain", help="Run the retraining flow")
    retrain_parser.add_argument("--force", action="store_true", help="Force retraining")
    
    # Deploy command
    deploy_parser = subparsers.add_parser("deploy", help="Create a scheduled deployment")
    
    # Feedback command
    feedback_parser = subparsers.add_parser("feedback", help="Manage feedback data")
    feedback_parser.add_argument("--action", choices=["stats", "export", "clear"], default="stats", help="Action to perform")
    feedback_parser.add_argument("--output", help="Output path for export action")
    feedback_parser.add_argument("--no-backup", action="store_true", help="Don't create backup when clearing")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Execute command
    if args.command == "setup":
        setup_mlflow_server()
    
    elif args.command == "train":
        include_feedback = not args.no_feedback
        save_local = not args.no_local_save
        run_id, metrics = train_and_log_model(
            include_feedback=include_feedback,
            save_local=save_local
        )
        if run_id:
            print(f"Model trained and logged successfully. Run ID: {run_id}")
    
    elif args.command == "drift":
        result = detect_drift()
        if result:
            print(f"Drift detected: {result['drift_detected']}")
            if result['drift_detected']:
                print("Concept drift detected! Consider retraining the model.")
            print(f"Drift report saved to: {result['report_path']}")
    
    elif args.command == "retrain":
        retraining_flow(force_retrain=args.force)
    
    elif args.command == "deploy":
        create_deployment()
    
    elif args.command == "feedback":
        collector = FeedbackCollector()
        
        if args.action == "stats":
            stats = collector.get_feedback_stats()
            print("Feedback Statistics:")
            for key, value in stats.items():
                print(f"  {key}: {value}")
        
        elif args.action == "export":
            output_path = collector.export_feedback(args.output)
            if output_path:
                print(f"Feedback data exported to: {output_path}")
        
        elif args.action == "clear":
            backup = not args.no_backup
            success = collector.clear_feedback(backup=backup)
            if success:
                print("Feedback data cleared successfully")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
