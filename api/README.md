# Fake News Detector API - Docker Setup

This directory contains the backend API for the Fake News Detector project.

## Running with Docker

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

### Starting the API

1. Navigate to the API directory:
   ```
   cd fake-news-detector/api
   ```

2. Build and start the API container:
   ```
   docker-compose up
   ```

3. The API will be available at http://localhost:8000

4. API documentation is available at http://localhost:8000/docs

### Stopping the API

Press `Ctrl+C` in the terminal where the API is running, or run:
```
docker-compose down
```

### Rebuilding the API

If you make changes to the code or dependencies, rebuild the container:
```
docker-compose up --build
```

## API Endpoints

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
