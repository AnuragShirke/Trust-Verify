# Fake News Detector with Trust Score

A comprehensive tool for detecting fake news and assessing the trustworthiness of news articles using machine learning and natural language processing techniques.

## Project Overview

This project consists of two main components:
1. **Backend API**: A FastAPI-based service that provides fake news detection and trust score calculation
2. **Frontend**: A React-based user interface built with Vite and Shadcn UI components for visualizing analysis results

## Features

- Fake news detection with confidence scores
- Trust score calculation based on multiple factors:
  - Source credibility
  - Content analysis
  - Language analysis
  - Fact verification
- Detailed analysis breakdown
- Clean, modern UI for result visualization
- User authentication system
- Real-time news analysis pipeline with Redis
- Dashboard for monitoring analyzed news

## How to Run the Project

### Option 1: Using Docker (Recommended)

The easiest way to run the project is using Docker and Docker Compose. Each component (backend and frontend) has its own Docker setup.

#### Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

#### Running the Backend with Docker

1. Navigate to the API directory:
   ```
   cd fake-news-detector/api
   ```

2. Build and start the API container:
   ```
   docker-compose up
   ```

3. The API will be available at http://localhost:8000
   - API Documentation: http://localhost:8000/docs

#### Running the Frontend with Docker

1. Navigate to the frontend directory:
   ```
   cd fake-news-detector/news-trust-visualizer
   ```

2. Build and start the frontend container:
   ```
   docker-compose up
   ```

3. The frontend will be available at http://localhost:5173

#### Stopping the Containers

Press `Ctrl+C` in the terminal where the containers are running, or run:
```
docker-compose down
```
in each respective directory.

### Option 2: Manual Setup

If you prefer to run the components manually, follow these instructions:

#### Prerequisites

- Python 3.8+ for the backend
- Node.js 16+ for the frontend
- Redis server (for real-time pipeline)
- Virtual environment (recommended)

#### Backend Setup

1. Navigate to the project root directory:
   ```
   cd fake-news-detector
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install the required Python packages:
   ```
   pip install -r api/requirements.txt
   ```

4. Start the API server:
   ```
   cd api
   uvicorn main:app --reload
   ```
   The API will be available at http://localhost:8000

#### Frontend Setup

1. Navigate to the frontend directory:
   ```
   cd fake-news-detector/news-trust-visualizer
   ```

2. Install the required Node.js packages:
   ```
   npm install
   ```

3. Start the development server:
   ```
   npm run dev
   ```
   The frontend will be available at http://localhost:5173

#### Real-Time Pipeline Setup (Optional)

The real-time pipeline is an optional component that can be used to automatically collect and analyze news articles. It's not required for the basic functionality of the application.

##### Option 1: Using Docker (Recommended)

1. Navigate to the pipeline directory:
   ```
   cd fake-news-detector/pipeline
   ```

2. Build and start the pipeline containers:
   ```
   docker-compose up
   ```

   This will start:
   - Redis server
   - Pipeline service (news collector, producer, consumer)
   - Dashboard service

3. The dashboard will be available at http://localhost:8080

4. To stop the pipeline:
   ```
   docker-compose down
   ```

##### Option 2: Manual Setup

If you prefer to set up the pipeline manually:

1. Install Redis:
   - **Windows**: Download and install from [Redis for Windows](https://github.com/microsoftarchive/redis/releases)
   - **Linux**: `sudo apt-get install redis-server`
   - **macOS**: `brew install redis`

2. Start Redis:
   ```
   redis-server
   ```

3. Install pipeline dependencies:
   ```
   pip install -r pipeline/requirements.txt
   ```

4. Run the pipeline components individually as needed:
   ```
   # Collect news articles
   python pipeline/news_collector.py

   # Push articles to Redis
   python pipeline/redis_producer.py

   # Process articles from Redis
   python pipeline/redis_consumer.py

   # Start the dashboard
   python pipeline/dashboard_server.py
   ```

5. Or run all components with the scheduler:
   ```
   python pipeline/run_pipeline.py --all
   ```

6. Access the dashboard:
   The dashboard will be available at http://localhost:8080

## API Endpoints

### Authentication Endpoints

- **POST /register**: Register a new user
  - Input: JSON with `username`, `email`, and `password` fields
  - Output: User information and access token

- **POST /login**: Login an existing user
  - Input: JSON with `username` and `password` fields
  - Output: User information and access token

### Analysis Endpoints

All analysis endpoints require authentication (JWT token in the Authorization header).

- **POST /predict**: Predicts whether a news article is real or fake
  - Input: JSON with a `text` field containing the article content
  - Output: Prediction (REAL/FAKE) and confidence score

- **POST /trust-score**: Calculates a trust score for a news article
  - Input: JSON with a `text` field containing the article content
  - Output: Trust score (0-100) and detailed breakdown of factors

- **POST /extract-url**: Extracts content from a URL
  - Input: JSON with a `url` field containing the URL to extract content from
  - Output: Extracted article content, title, source, and source credibility

- **POST /analyze-url**: Analyzes a news article from a URL
  - Input: JSON with a `url` field containing the URL to analyze
  - Output: Prediction, trust score, and extracted article content

## Project Structure

```
fake-news-detector/
├── api/                  # Backend API
│   ├── main.py           # FastAPI application
│   ├── url_scraper.py    # URL content extraction module
│   ├── auth.py           # Authentication module
│   ├── database.py       # Database operations
│   ├── models.py         # Data models
│   ├── generate_models.py # Database model generation script
│   ├── Dockerfile        # Docker configuration for API
│   ├── docker-compose.yml # Docker Compose for API
│   ├── requirements.txt  # Python dependencies for API
│   ├── README.md         # API documentation
│   ├── static/           # Static files for the API
│   ├── templates/        # HTML templates for the API
│   ├── cache/            # Cache directory for URL extraction
│   └── db/               # Database files
├── data/                 # Training and test data
│   └── raw/              # Raw training data
├── mlops/                # MLOps components
│   ├── config.py         # Configuration settings
│   ├── data_prep.py      # Data preparation utilities
│   ├── drift_detection.py # Concept drift detection
│   ├── feedback_collector.py # Feedback collection and management
│   ├── init_mlops.py     # MLOps initialization script
│   ├── mlflow_utils.py   # MLflow utilities
│   ├── run_mlops.py      # Main script for running MLOps tasks
│   ├── scheduled_retraining.py # Scheduled retraining with Prefect
│   ├── train_model.py    # Enhanced model training script
│   ├── docker-compose.yml # Docker Compose for MLflow and Prefect
│   └── README.md         # MLOps documentation
├── model/                # Trained ML models
│   ├── classifier.pkl    # Trained classifier
│   ├── tfidf_vectorizer.pkl  # TF-IDF vectorizer
│   └── train_model.py    # Model training script
├── news-trust-visualizer/ # Frontend application
│   ├── public/           # Static assets
│   ├── src/              # Source code
│   │   ├── components/   # UI components
│   │   │   └── ui/       # Shadcn UI components
│   │   ├── context/      # React context providers
│   │   │   ├── AppContext.tsx # Application state context
│   │   │   └── AuthContext.tsx # Authentication context
│   │   ├── hooks/        # Custom React hooks
│   │   ├── lib/          # Utility functions
│   │   ├── pages/        # Page components
│   │   └── App.tsx       # Main application component
│   ├── Dockerfile        # Docker configuration for frontend
│   ├── docker-compose.yml # Docker Compose for frontend
│   ├── README.md         # Frontend documentation
│   └── package.json      # Node.js dependencies
├── pipeline/             # Real-time news pipeline
│   ├── news_collector.py # News collector script
│   ├── redis_producer.py # Redis producer script
│   ├── redis_consumer.py # Redis consumer script
│   ├── dashboard_server.py # Real-time dashboard server
│   ├── realtime_dashboard.py # Real-time dashboard UI
│   ├── scheduler.py      # Scheduler for periodic tasks
│   ├── logger.py         # Logging configuration
│   ├── run_pipeline.py   # Main script to run the pipeline
│   ├── Dockerfile        # Docker configuration for pipeline
│   ├── Dockerfile.dashboard # Docker configuration for dashboard
│   ├── docker-compose.yml # Docker Compose for pipeline
│   ├── logs/             # Log directory
│   ├── requirements.txt  # Python dependencies for pipeline
│   └── README.md         # Pipeline documentation
├── docker-compose.yml    # Root Docker Compose file for all services
├── run_mlops.sh          # Shell script for running MLOps tasks (Linux/macOS)
├── run_mlops.bat         # Batch script for running MLOps tasks (Windows)
├── README.md             # Project documentation
├── requirements.txt      # Python dependencies for the project
├── .dockerignore         # Docker ignore file
└── .gitignore            # Git ignore file
```

## Running the Project

### Using Docker Compose (Recommended)

The easiest way to run the entire project is using the root Docker Compose file:

```bash
# Build and start all services
docker-compose up -d

# The services will be available at:
# - API: http://localhost:8000
# - Frontend: http://localhost:5173
# - Pipeline Dashboard: http://localhost:8080
# - MLflow UI: http://localhost:5000
```

### Running Individual Components

#### API

```bash
# Navigate to the API directory
cd api

# Build and start the API container
docker-compose up -d

# The API will be available at http://localhost:8000
```

#### Frontend

```bash
# Navigate to the frontend directory
cd news-trust-visualizer

# Install dependencies
npm install

# Start the development server
npm run dev

# The frontend will be available at http://localhost:5173
```

#### Pipeline

```bash
# Navigate to the pipeline directory
cd pipeline

# Build and start the pipeline containers
docker-compose up -d

# The dashboard will be available at http://localhost:8080
```

## Real-time News Analysis Pipeline

The project includes a real-time news analysis pipeline that allows for continuous ingestion and analysis of news articles from various sources. The pipeline uses Redis Streams for the message queue.

### Redis Pipeline

The Redis-based pipeline is simple to set up and requires minimal resources.

#### Components

- **News Collector**: Fetches news articles from RSS feeds and optionally from NewsAPI
- **Redis Producer**: Pushes collected articles to a Redis stream
- **Redis Consumer**: Processes articles from the Redis stream and analyzes them
- **Dashboard**: Real-time visualization of processed articles
- **Scheduler**: Runs the collector and producer at regular intervals

#### Running the Redis Pipeline

The easiest way to run the Redis pipeline is using Docker:

```bash
# Navigate to the pipeline directory
cd pipeline

# Build and start the pipeline containers
docker-compose up -d

# The dashboards will be available at:
# - Standard dashboard: http://localhost:8080
# - Real-time dashboard: http://localhost:8081
```

You can also use the root docker-compose.yml file to start all services including the pipeline:

```bash
# From the project root
docker-compose up -d

# The dashboards will be available at:
# - Standard dashboard: http://localhost:8080
# - Real-time dashboard: http://localhost:8081
```

#### Redis Components

- **Producer**: Sends news articles to the `raw-news` stream
- **Consumer**: Processes news articles from the `raw-news` stream
- **Analyzer**: Analyzes news articles and sends results to the `analyzed-news` stream
- **News Scraper**: Collects news articles from various sources

## Authentication System

The application now includes a comprehensive user authentication system:

1. **User Registration and Login**:
   - Secure user registration with email verification
   - Password hashing using bcrypt
   - JWT (JSON Web Token) based authentication
   - Token refresh mechanism

2. **Protected Resources**:
   - All analysis endpoints require authentication
   - User-specific history and preferences
   - Role-based access control for admin functions

3. **Security Features**:
   - Password strength validation
   - Rate limiting for login attempts
   - Token expiration and refresh mechanism
   - CORS protection

## URL Scraping Functionality

The API includes URL scraping functionality, which allows users to analyze news articles directly from URLs. This feature:

1. Extracts content from news article URLs using multiple methods:
   - Newspaper3k library for comprehensive article extraction
   - Trafilatura for robust content extraction
   - Readability for fallback extraction

2. Provides source credibility assessment based on the domain
   - Known trusted domains receive higher credibility scores
   - Known fake news domains receive lower credibility scores

3. Integrates with the existing analysis pipeline
   - Extracted content is analyzed using the same ML model
   - Trust scores are calculated with additional domain-based factors

### Example Usage

```bash
# Register a new user
curl -X POST "http://localhost:8000/register" \
     -H "Content-Type: application/json" \
     -d '{"username": "testuser", "email": "test@example.com", "password": "securepassword"}'

# Login to get an access token
curl -X POST "http://localhost:8000/login" \
     -H "Content-Type: application/json" \
     -d '{"username": "testuser", "password": "securepassword"}'

# Store the token from the response
TOKEN="your_access_token_here"

# Extract content from a URL (authenticated)
curl -X POST "http://localhost:8000/extract-url" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer $TOKEN" \
     -d '{"url": "https://www.bbc.com/news/science-environment-56837908"}'

# Analyze a news article from a URL (authenticated)
curl -X POST "http://localhost:8000/analyze-url" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer $TOKEN" \
     -d '{"url": "https://www.bbc.com/news/science-environment-56837908"}'
```

## MLOps Features

The project now includes MLOps features for model versioning, tracking, scheduled retraining, concept drift detection, and feedback integration.

### MLOps Components

- **Model Versioning & Tracking**: Using MLflow to track model versions, parameters, metrics, and artifacts
- **Scheduled Retraining**: Using Prefect to schedule and orchestrate model retraining
- **Concept Drift Detection**: Monitoring for changes in data distribution and model performance
- **Feedback Loop Integration**: Collecting and incorporating user feedback for model improvement

### Running MLOps Components

#### Using Docker (Recommended)

The easiest way to run the MLOps components is using Docker:

```bash
# Start all services including MLflow and API with MLOps integration
docker-compose up -d

# Access MLflow UI
# Open http://localhost:5000 in your browser
```

#### Using the MLOps Scripts

For Windows:
```bash
# Initialize the MLOps environment
run_mlops.bat init

# Train a new model
run_mlops.bat train

# Check for concept drift
run_mlops.bat drift

# Force model retraining
run_mlops.bat retrain
```

For Linux/macOS:
```bash
# Make the script executable
chmod +x run_mlops.sh

# Initialize the MLOps environment
./run_mlops.sh init

# Train a new model
./run_mlops.sh train

# Check for concept drift
./run_mlops.sh drift

# Force model retraining
./run_mlops.sh retrain
```

## Future Enhancements

- Enhanced user profile and history tracking
- Advanced trust score algorithm with machine learning improvements
- Mobile application for on-the-go news verification
- Integration with social media platforms for direct analysis
- Customizable trust score factors based on user preferences
- Browser extension for real-time analysis while browsing
- Expanded real-time news monitoring capabilities

## Deployment Guide

This project can be deployed using various cloud services. The recommended setup is:
- Backend API: Render.com
- Frontend: Vercel
- Redis Pipeline: Render.com
- MLOps Pipeline: Render.com

### Backend Deployment on Render

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Select the `fake-news-detector/api` directory
4. Set the following configuration:
   - Environment: Docker
   - Build Command: (leave empty, Docker will handle it)
   - Start Command: (leave empty, Docker will handle it)
   - Add the following environment variables:
     - `PORT`: 8000
     - `CORS_ORIGINS`: https://trustverify.vercel.app,http://localhost:5173,http://localhost:8080
     - `MLFLOW_TRACKING_URI`: (Your MLflow tracking URI or leave as default)

### Frontend Deployment on Vercel

1. Create a new project on Vercel
2. Connect your GitHub repository
3. Set the following configuration:
   - Framework Preset: Vite
   - Root Directory: fake-news-detector/news-trust-visualizer
   - Build Command: npm run build
   - Output Directory: dist
   - Install Command: npm install
   - Add the following environment variables:
     - `VITE_API_URL`: (Your Render API URL, e.g., https://trustverify-api.onrender.com)

### Redis Pipeline Deployment on Render

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Select the `fake-news-detector/pipeline` directory
4. Set the following configuration:
   - Environment: Docker
   - Build Command: (leave empty, Docker will handle it)
   - Start Command: (leave empty, Docker will handle it)
   - Add the following environment variables:
     - `PORT`: 8080
     - `REDIS_URL`: (Your Redis URL if using a hosted Redis service)
     - `REDIS_HOST`: (Your Redis host if not using REDIS_URL)
     - `REDIS_PORT`: (Your Redis port if not using REDIS_URL)
     - `REDIS_PASSWORD`: (Your Redis password if required)
     - `API_BASE_URL`: (Your Render API URL, e.g., https://trustverify-api.onrender.com)

### MLOps Pipeline Deployment on Render

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Select the `fake-news-detector/mlops` directory
4. Set the following configuration:
   - Environment: Docker
   - Build Command: (leave empty, Docker will handle it)
   - Start Command: (leave empty, Docker will handle it)
   - Add the following environment variables:
     - `PORT`: 5000
     - `MLFLOW_TRACKING_URI`: (Your MLflow tracking URI)
     - `MLFLOW_ARTIFACT_ROOT`: (Your artifact storage path)
     - `MLFLOW_BACKEND_STORE_URI`: (Your backend store URI)
     - `RETRAINING_SCHEDULE`: (Cron schedule for retraining, e.g., 0 0 * * *)
     - `DRIFT_CHECK_SCHEDULE`: (Cron schedule for drift detection, e.g., 0 */6 * * *)

### Notes on Redis Deployment

For Redis, you have two options:
1. Use a managed Redis service like Redis Cloud, Upstash, or AWS ElastiCache
2. Deploy Redis on Render using the Docker Compose configuration

For production, a managed Redis service is recommended for better reliability and scalability.

## License

MIT