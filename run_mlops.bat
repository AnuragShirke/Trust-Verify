@echo off
REM Run MLOps pipeline for the Fake News Detector project

REM Function to display help message
:show_help
    echo Usage: run_mlops.bat [OPTION]
    echo Run MLOps pipeline for the Fake News Detector project.
    echo.
    echo Options:
    echo   init        Initialize the MLOps environment
    echo   train       Train and log a new model
    echo   drift       Check for concept drift
    echo   retrain     Force model retraining
    echo   deploy      Create a scheduled deployment
    echo   feedback    Manage feedback data
    echo   mlflow      Start the MLflow server
    echo   retraining  Start the retraining service
    echo   all         Start all MLOps services
    echo   help        Display this help message
    echo.
    goto :eof

REM Check if Docker is running
:check_docker
    docker info > nul 2>&1
    if %ERRORLEVEL% neq 0 (
        echo Error: Docker is not running. Please start Docker and try again.
        exit /b 1
    )
    goto :eof

REM Initialize the MLOps environment
:init_mlops
    echo Initializing MLOps environment...
    cd mlops
    python init_mlops.py
    cd ..
    goto :eof

REM Train and log a new model
:train_model
    echo Training and logging a new model...
    cd mlops
    python run_mlops.py train
    cd ..
    goto :eof

REM Check for concept drift
:check_drift
    echo Checking for concept drift...
    cd mlops
    python run_mlops.py drift
    cd ..
    goto :eof

REM Force model retraining
:force_retrain
    echo Forcing model retraining...
    cd mlops
    python run_mlops.py retrain --force
    cd ..
    goto :eof

REM Create a scheduled deployment
:create_deployment
    echo Creating a scheduled deployment...
    cd mlops
    python run_mlops.py deploy
    cd ..
    goto :eof

REM Manage feedback data
:manage_feedback
    echo Managing feedback data...
    cd mlops
    python run_mlops.py feedback --action stats
    cd ..
    goto :eof

REM Start the MLflow server
:start_mlflow
    echo Starting MLflow server...
    call :check_docker
    docker-compose -f mlops/docker-compose.yml up -d mlflow
    echo MLflow server is running at http://localhost:5000
    goto :eof

REM Start the retraining service
:start_retraining
    echo Starting retraining service...
    call :check_docker
    docker-compose -f mlops/docker-compose.yml up -d retraining
    echo Retraining service is running
    goto :eof

REM Start all MLOps services
:start_all
    echo Starting all MLOps services...
    call :check_docker
    docker-compose -f mlops/docker-compose.yml up -d
    echo MLflow server is running at http://localhost:5000
    echo Retraining service is running
    echo Drift detection service is running
    goto :eof

REM Main script logic
if "%1"=="" goto show_help
if "%1"=="init" call :init_mlops & goto :eof
if "%1"=="train" call :train_model & goto :eof
if "%1"=="drift" call :check_drift & goto :eof
if "%1"=="retrain" call :force_retrain & goto :eof
if "%1"=="deploy" call :create_deployment & goto :eof
if "%1"=="feedback" call :manage_feedback & goto :eof
if "%1"=="mlflow" call :start_mlflow & goto :eof
if "%1"=="retraining" call :start_retraining & goto :eof
if "%1"=="all" call :start_all & goto :eof
if "%1"=="help" goto show_help
if "%1"=="--help" goto show_help
if "%1"=="-h" goto show_help

echo Unknown option: %1
call :show_help
exit /b 1
