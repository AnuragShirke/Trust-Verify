# MLOps for Fake News Detector

This directory contains MLOps components for the Fake News Detector project, including model versioning, tracking, scheduled retraining, concept drift detection, and feedback integration.

## Components

- **Model Versioning & Tracking**: Using MLflow to track model versions, parameters, metrics, and artifacts
- **Scheduled Retraining**: Using Prefect to schedule and orchestrate model retraining
- **Concept Drift Detection**: Monitoring for changes in data distribution and model performance
- **Feedback Loop Integration**: Collecting and incorporating user feedback for model improvement

## Setup

### Prerequisites

- Python 3.8+
- Docker and Docker Compose (for MLflow and Prefect servers)

### Installation

1. Install the required dependencies:

```bash
pip install -r ../requirements.txt
```

2. Start the MLflow and Prefect servers:

```bash
docker-compose up -d
```

## Usage

### Model Training and Tracking

Train a new model and log it with MLflow:

```bash
python run_mlops.py train
```

### Concept Drift Detection

Check for concept drift in the model:

```bash
python run_mlops.py drift
```

### Scheduled Retraining

Create a scheduled deployment for model retraining:

```bash
python run_mlops.py deploy
```

Force a model retraining:

```bash
python run_mlops.py retrain --force
```

### Feedback Management

View feedback statistics:

```bash
python run_mlops.py feedback --action stats
```

Export feedback data:

```bash
python run_mlops.py feedback --action export --output feedback_export.csv
```

Clear feedback data (with backup):

```bash
python run_mlops.py feedback --action clear
```

## MLflow UI

Access the MLflow UI at http://localhost:5000 to view model versions, parameters, metrics, and artifacts.

## Prefect UI

Access the Prefect UI at http://localhost:4200 to view and manage scheduled deployments and flow runs.

## Integration with API

The MLOps components are integrated with the API through the `mlops_integration.py` module, which provides functions for:

- Loading models from MLflow
- Submitting feedback
- Checking for concept drift
- Getting model information

## Directory Structure

```
mlops/
├── config.py                # Configuration settings
├── data_prep.py             # Data preparation utilities
├── drift_detection.py       # Concept drift detection
├── feedback_collector.py    # Feedback collection and management
├── mlflow_utils.py          # MLflow utilities
├── run_mlops.py             # Main script for running MLOps tasks
├── scheduled_retraining.py  # Scheduled retraining with Prefect
├── train_model.py           # Enhanced model training script
├── docker-compose.yml       # Docker Compose for MLflow and Prefect
└── README.md                # This file
```
