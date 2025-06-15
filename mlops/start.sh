#!/bin/sh

# Initialize data directory if needed
if [ ! -s "/app/data/processed/train.csv" ]; then
    echo "Warning: No training data found. Service will wait for data to be available."
fi

# Start MLflow tracking server
mlflow server \
    --host 0.0.0.0 \
    --port $PORT \
    --backend-store-uri $DATABASE_URL \
    --default-artifact-root $ARTIFACT_ROOT &

# Start scheduled retraining in the background
python /app/mlops/scheduled_retraining.py --deploy &
RETRAINING_PID=$!

# Start drift detection in the background
python /app/mlops/drift_detection.py &
DRIFT_PID=$!

# Function to handle shutdown
cleanup() {
    echo "Shutting down services..."
    kill $RETRAINING_PID
    kill $DRIFT_PID
    exit 0
}

# Set up signal handling
trap cleanup SIGTERM SIGINT

# Keep the script running
while true; do
    sleep 10
done
