#!/bin/bash

# Run MLOps pipeline for the Fake News Detector project

# Function to display help message
show_help() {
    echo "Usage: ./run_mlops.sh [OPTION]"
    echo "Run MLOps pipeline for the Fake News Detector project."
    echo ""
    echo "Options:"
    echo "  init        Initialize the MLOps environment"
    echo "  train       Train and log a new model"
    echo "  drift       Check for concept drift"
    echo "  retrain     Force model retraining"
    echo "  deploy      Create a scheduled deployment"
    echo "  feedback    Manage feedback data"
    echo "  mlflow      Start the MLflow server"
    echo "  retraining  Start the retraining service"
    echo "  all         Start all MLOps services"
    echo "  help        Display this help message"
    echo ""
}

# Check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        echo "Error: Docker is not running. Please start Docker and try again."
        exit 1
    fi
}

# Initialize the MLOps environment
init_mlops() {
    echo "Initializing MLOps environment..."
    cd mlops
    python init_mlops.py
    cd ..
}

# Train and log a new model
train_model() {
    echo "Training and logging a new model..."
    cd mlops
    python run_mlops.py train
    cd ..
}

# Check for concept drift
check_drift() {
    echo "Checking for concept drift..."
    cd mlops
    python run_mlops.py drift
    cd ..
}

# Force model retraining
force_retrain() {
    echo "Forcing model retraining..."
    cd mlops
    python run_mlops.py retrain --force
    cd ..
}

# Create a scheduled deployment
create_deployment() {
    echo "Creating a scheduled deployment..."
    cd mlops
    python run_mlops.py deploy
    cd ..
}

# Manage feedback data
manage_feedback() {
    echo "Managing feedback data..."
    cd mlops
    python run_mlops.py feedback --action stats
    cd ..
}

# Start the MLflow server
start_mlflow() {
    echo "Starting MLflow server..."
    check_docker
    docker-compose -f mlops/docker-compose.yml up -d mlflow
    echo "MLflow server is running at http://localhost:5000"
}

# Start the retraining service
start_retraining() {
    echo "Starting retraining service..."
    check_docker
    docker-compose -f mlops/docker-compose.yml up -d retraining
    echo "Retraining service is running"
}

# Start all MLOps services
start_all() {
    echo "Starting all MLOps services..."
    check_docker
    docker-compose -f mlops/docker-compose.yml up -d
    echo "MLflow server is running at http://localhost:5000"
    echo "Retraining service is running"
    echo "Drift detection service is running"
}

# Main script logic
case "$1" in
    init)
        init_mlops
        ;;
    train)
        train_model
        ;;
    drift)
        check_drift
        ;;
    retrain)
        force_retrain
        ;;
    deploy)
        create_deployment
        ;;
    feedback)
        manage_feedback
        ;;
    mlflow)
        start_mlflow
        ;;
    retraining)
        start_retraining
        ;;
    all)
        start_all
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo "Unknown option: $1"
        show_help
        exit 1
        ;;
esac

exit 0
