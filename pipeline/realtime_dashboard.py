#!/usr/bin/env python
"""
Real-Time Dashboard Server (Robust Version)

This script provides a FastAPI server for the Fake News Detector dashboard
with real-time updates using Server-Sent Events (SSE) instead of WebSockets.
"""

import os
import json
import time
import logging
import asyncio
import redis
from datetime import datetime
from typing import List, Dict, Any
import uvicorn
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import HTMLResponse, StreamingResponse
from sse_starlette.sse import EventSourceResponse

# Configure logging
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/realtime_dashboard.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("realtime_dashboard")

# Redis configuration
REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
REDIS_DB = int(os.environ.get("REDIS_DB", 0))
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD", None)
REDIS_STREAM_NAME = os.environ.get("REDIS_STREAM_NAME", "news_articles")

# Server configuration
HOST = "0.0.0.0"
PORT = int(os.environ.get("PORT", 8080))

# Create the FastAPI app
app = FastAPI(title="Fake News Detector Real-Time Dashboard")

# Create a Redis connection pool
redis_pool = redis.ConnectionPool(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    password=REDIS_PASSWORD,
    decode_responses=True
)

# In-memory storage for demo data
articles = []
sources = {}
trust_scores = {
    'High Trust (70-100)': 0,
    'Medium Trust (50-69)': 0,
    'Low Trust (0-49)': 0
}

# Function to generate demo data
async def generate_demo_data():
    """Generate demo data for testing the dashboard."""
    logger.info("Starting demo data generator")

    demo_sources = ["CNN", "BBC", "Reuters", "AP News", "The Guardian"]
    demo_titles = [
        "Breaking News: Major Policy Change Announced",
        "Scientists Discover New Species in Amazon Rainforest",
        "Tech Company Launches Revolutionary Product",
        "Global Summit Addresses Climate Change Concerns",
        "Sports Team Wins Championship in Dramatic Fashion"
    ]

    while True:
        try:
            # Generate a random article
            import random

            source = random.choice(demo_sources)
            title = random.choice(demo_titles)
            trust_score = random.randint(30, 95)
            prediction = "REAL" if trust_score > 60 else "FAKE"

            # Create article object
            article = {
                "title": title,
                "source": source,
                "url": f"https://example.com/{source.lower()}/{int(time.time())}",
                "timestamp": datetime.now().isoformat(),
                "trustScore": trust_score,
                "prediction": prediction
            }

            # Update in-memory storage
            articles.insert(0, article)
            if len(articles) > 100:  # Keep only the latest 100 articles
                articles.pop()

            sources[source] = sources.get(source, 0) + 1

            # Update trust score distribution
            if trust_score >= 70:
                trust_scores['High Trust (70-100)'] += 1
            elif trust_score >= 50:
                trust_scores['Medium Trust (50-69)'] += 1
            else:
                trust_scores['Low Trust (0-49)'] += 1

            # Publish to Redis for real clients
            redis_client = redis.Redis(connection_pool=redis_pool)
            redis_client.xadd(
                REDIS_STREAM_NAME,
                {
                    "title": title,
                    "source": source,
                    "url": article["url"],
                    "timestamp": article["timestamp"],
                    "analysis": json.dumps({
                        "score": trust_score,
                        "prediction": prediction
                    })
                }
            )

            logger.debug(f"Generated demo article: {title}")

            # Wait before generating the next article
            await asyncio.sleep(10)  # Generate a new article every 10 seconds

        except Exception as e:
            logger.error(f"Error in demo data generator: {str(e)}")
            await asyncio.sleep(5)  # Wait before retrying

# Redis listener task
async def redis_listener():
    """Listen for new messages in the Redis stream."""
    logger.info("Starting Redis listener")

    # Create a Redis client
    redis_client = redis.Redis(connection_pool=redis_pool)

    # Keep track of the last ID we've seen
    last_id = "0"

    while True:
        try:
            # Read new messages from the stream
            messages = redis_client.xread({REDIS_STREAM_NAME: last_id}, count=10, block=1000)

            if messages:
                for stream_name, stream_messages in messages:
                    for message_id, message_data in stream_messages:
                        # Update the last ID
                        last_id = message_id

                        # Process the message
                        logger.debug(f"Received message {message_id}")

                        # Extract data
                        title = message_data.get("title", "Untitled")
                        source = message_data.get("source", "Unknown")
                        url = message_data.get("url", "#")
                        timestamp = message_data.get("timestamp", datetime.now().isoformat())

                        # Parse analysis data if available
                        analysis_data = {}
                        if "analysis" in message_data:
                            try:
                                analysis_data = json.loads(message_data["analysis"])
                            except:
                                analysis_data = {}

                        trust_score = analysis_data.get("score", 0)
                        prediction = analysis_data.get("prediction", "UNKNOWN")

                        # Create article object
                        article = {
                            "title": title,
                            "source": source,
                            "url": url,
                            "timestamp": timestamp,
                            "trustScore": trust_score,
                            "prediction": prediction
                        }

                        # Update in-memory storage
                        articles.insert(0, article)
                        if len(articles) > 100:  # Keep only the latest 100 articles
                            articles.pop()

                        sources[source] = sources.get(source, 0) + 1

                        # Update trust score distribution
                        if trust_score >= 70:
                            trust_scores['High Trust (70-100)'] += 1
                        elif trust_score >= 50:
                            trust_scores['Medium Trust (50-69)'] += 1
                        else:
                            trust_scores['Low Trust (0-49)'] += 1

        except Exception as e:
            logger.error(f"Error in Redis listener: {str(e)}")
            await asyncio.sleep(5)  # Wait before retrying

# SSE endpoint for real-time updates
@app.get("/events")
async def events(request: Request):
    """Server-Sent Events endpoint for real-time updates."""
    async def event_generator():
        # Send initial data
        yield {
            "event": "init",
            "data": json.dumps({
                "articles": articles[:10],  # Send only the 10 most recent articles
                "sources": sources,
                "trustScores": trust_scores
            })
        }

        # Keep track of the number of articles to detect changes
        last_article_count = len(articles)

        # Send updates every second
        while True:
            # Check if client is still connected
            if await request.is_disconnected():
                logger.info("Client disconnected from SSE")
                break

            # Check if there are new articles
            if len(articles) > last_article_count:
                # Send only the new articles
                new_articles = articles[:len(articles) - last_article_count]
                last_article_count = len(articles)

                yield {
                    "event": "update",
                    "data": json.dumps({
                        "articles": new_articles,
                        "sources": sources,
                        "trustScores": trust_scores
                    })
                }

            # Wait before checking again
            await asyncio.sleep(1)

    return EventSourceResponse(event_generator())

# Simple test endpoint
@app.get("/ping")
async def ping():
    return {"status": "ok", "message": "Real-time dashboard is running"}

# Get dashboard data
@app.get("/api/data")
async def get_data():
    return {
        "articles": articles[:10],  # Send only the 10 most recent articles
        "sources": sources,
        "trustScores": trust_scores,
        "stats": {
            "totalArticles": len(articles),
            "fakeNewsCount": sum(1 for a in articles if a["prediction"] == "FAKE"),
            "avgTrustScore": sum(a["trustScore"] for a in articles) / max(1, len(articles))
        }
    }

# Main dashboard HTML
@app.get("/", response_class=HTMLResponse)
async def get_dashboard(background_tasks: BackgroundTasks):
    # Start the demo data generator and Redis listener if they're not already running
    background_tasks.add_task(generate_demo_data)
    background_tasks.add_task(redis_listener)

    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Fake News Detector - Real-Time Dashboard</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <script src="https://cdn.tailwindcss.com"></script>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            .article-card {
                transition: all 0.3s ease;
            }
            .article-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
            }
        </style>
    </head>
    <body class="bg-gray-100 min-h-screen">
        <div class="container mx-auto px-4 py-8">
            <header class="mb-8">
                <div class="flex justify-between items-center">
                    <div>
                        <h1 class="text-3xl font-bold text-gray-800">Fake News Detector</h1>
                        <h2 class="text-xl text-gray-600">Real-Time Dashboard</h2>
                    </div>
                    <div class="flex items-center space-x-2">
                        <span class="text-sm">Connection:</span>
                        <span id="connection-status" class="text-xs px-2 py-1 rounded-full bg-yellow-100 text-yellow-800">
                            Connecting...
                        </span>
                    </div>
                </div>
            </header>

            <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
                <div class="bg-white rounded-lg shadow p-6">
                    <h3 class="text-lg font-semibold mb-4">Articles Processed</h3>
                    <div class="text-4xl font-bold text-blue-600" id="articles-count">0</div>
                </div>

                <div class="bg-white rounded-lg shadow p-6">
                    <h3 class="text-lg font-semibold mb-4">Fake News Detected</h3>
                    <div class="text-4xl font-bold text-red-600" id="fake-count">0</div>
                </div>

                <div class="bg-white rounded-lg shadow p-6">
                    <h3 class="text-lg font-semibold mb-4">Average Trust Score</h3>
                    <div class="text-4xl font-bold text-green-600" id="avg-trust-score">0%</div>
                </div>
            </div>

            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
                <div class="bg-white rounded-lg shadow p-6">
                    <h3 class="text-lg font-semibold mb-4">Trust Score Distribution</h3>
                    <canvas id="trust-score-chart" height="200"></canvas>
                </div>

                <div class="bg-white rounded-lg shadow p-6">
                    <h3 class="text-lg font-semibold mb-4">Source Credibility</h3>
                    <canvas id="source-chart" height="200"></canvas>
                </div>
            </div>

            <div class="bg-white rounded-lg shadow p-6 mb-8">
                <h3 class="text-lg font-semibold mb-4">Recent Articles</h3>
                <div id="recent-articles" class="space-y-4">
                    <div class="text-center text-gray-500 py-8">Waiting for articles...</div>
                </div>
            </div>
        </div>

        <script>
            // Data storage
            const articles = [];
            const sources = {};
            const trustScores = {
                'High Trust (70-100)': 0,
                'Medium Trust (50-69)': 0,
                'Low Trust (0-49)': 0
            };

            // Charts
            let trustScoreChart;
            let sourceChart;

            // Initialize charts
            function initCharts() {
                const trustScoreCtx = document.getElementById('trust-score-chart').getContext('2d');
                trustScoreChart = new Chart(trustScoreCtx, {
                    type: 'pie',
                    data: {
                        labels: Object.keys(trustScores),
                        datasets: [{
                            data: Object.values(trustScores),
                            backgroundColor: [
                                'rgba(72, 187, 120, 0.7)',
                                'rgba(237, 137, 54, 0.7)',
                                'rgba(229, 62, 62, 0.7)'
                            ],
                            borderColor: [
                                'rgba(72, 187, 120, 1)',
                                'rgba(237, 137, 54, 1)',
                                'rgba(229, 62, 62, 1)'
                            ],
                            borderWidth: 1
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: {
                                position: 'bottom'
                            }
                        }
                    }
                });

                const sourceCtx = document.getElementById('source-chart').getContext('2d');
                sourceChart = new Chart(sourceCtx, {
                    type: 'bar',
                    data: {
                        labels: [],
                        datasets: [{
                            label: 'Articles',
                            data: [],
                            backgroundColor: 'rgba(66, 153, 225, 0.7)',
                            borderColor: 'rgba(66, 153, 225, 1)',
                            borderWidth: 1
                        }]
                    },
                    options: {
                        responsive: true,
                        scales: {
                            y: {
                                beginAtZero: true,
                                ticks: {
                                    stepSize: 1
                                }
                            }
                        },
                        plugins: {
                            legend: {
                                display: false
                            }
                        }
                    }
                });
            }

            // Update charts
            function updateCharts() {
                // Update trust score chart
                trustScoreChart.data.datasets[0].data = Object.values(trustScores);
                trustScoreChart.update();

                // Update source chart
                const sourceLabels = Object.keys(sources).slice(0, 10);
                const sourceData = sourceLabels.map(label => sources[label]);

                sourceChart.data.labels = sourceLabels;
                sourceChart.data.datasets[0].data = sourceData;
                sourceChart.update();
            }

            // Update metrics
            function updateMetrics() {
                document.getElementById('articles-count').textContent = articles.length;

                const fakeCount = articles.filter(a => a.prediction === 'FAKE').length;
                document.getElementById('fake-count').textContent = fakeCount;

                const totalTrustScore = articles.reduce((sum, a) => sum + (a.trustScore || 0), 0);
                const avgTrustScore = articles.length > 0 ? Math.round(totalTrustScore / articles.length) : 0;
                document.getElementById('avg-trust-score').textContent = `${avgTrustScore}%`;
            }

            // Update recent articles
            function updateRecentArticles() {
                const recentArticlesEl = document.getElementById('recent-articles');

                if (articles.length === 0) {
                    recentArticlesEl.innerHTML = '<div class="text-center text-gray-500">Waiting for articles...</div>';
                    return;
                }

                // Get the 10 most recent articles
                const recentArticles = articles.slice(0, 10);

                // Clear the container
                recentArticlesEl.innerHTML = '';

                // Add each article
                recentArticles.forEach(article => {
                    const trustScoreClass =
                        article.trustScore >= 70 ? 'bg-green-100 text-green-800' :
                        article.trustScore >= 50 ? 'bg-yellow-100 text-yellow-800' :
                        'bg-red-100 text-red-800';

                    const predictionClass =
                        article.prediction === 'REAL' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800';

                    const articleEl = document.createElement('div');
                    articleEl.className = 'article-card bg-white border rounded-lg p-4 hover:shadow-md';
                    articleEl.innerHTML = `
                        <div class="flex justify-between items-start">
                            <div>
                                <h4 class="font-semibold">${article.title || 'Untitled'}</h4>
                                <p class="text-sm text-gray-600">${article.source || 'Unknown source'}</p>
                            </div>
                            <div class="flex space-x-2">
                                <span class="px-2 py-1 rounded-full text-xs font-semibold ${predictionClass}">
                                    ${article.prediction}
                                </span>
                                <span class="px-2 py-1 rounded-full text-xs font-semibold ${trustScoreClass}">
                                    ${article.trustScore}%
                                </span>
                            </div>
                        </div>
                    `;

                    recentArticlesEl.appendChild(articleEl);
                });
            }

            // Process new articles
            function processArticles(newArticles) {
                // Add new articles to the beginning of the array
                articles.unshift(...newArticles);

                // Limit to 100 articles
                if (articles.length > 100) {
                    articles.splice(100);
                }

                // Update UI
                updateMetrics();
                updateRecentArticles();
                updateCharts();
            }

            // Update sources and trust scores
            function updateData(data) {
                // Update sources
                Object.entries(data.sources).forEach(([source, count]) => {
                    sources[source] = count;
                });

                // Update trust scores
                Object.entries(data.trustScores).forEach(([level, count]) => {
                    trustScores[level] = count;
                });

                // Update charts
                updateCharts();
            }

            // Initialize the dashboard
            document.addEventListener('DOMContentLoaded', function() {
                // Initialize charts
                initCharts();

                // Connect to SSE endpoint
                connectSSE();
            });

            // Connect to Server-Sent Events
            function connectSSE() {
                const statusEl = document.getElementById('connection-status');
                statusEl.textContent = 'Connecting...';
                statusEl.className = 'text-xs px-2 py-1 rounded-full bg-yellow-100 text-yellow-800';

                const eventSource = new EventSource('/events');

                eventSource.onopen = function() {
                    console.log('SSE connection established');
                    statusEl.textContent = 'Connected';
                    statusEl.className = 'text-xs px-2 py-1 rounded-full bg-green-100 text-green-800';
                };

                eventSource.onerror = function(error) {
                    console.error('SSE connection error:', error);
                    statusEl.textContent = 'Disconnected';
                    statusEl.className = 'text-xs px-2 py-1 rounded-full bg-red-100 text-red-800';

                    // Try to reconnect after a delay
                    setTimeout(connectSSE, 5000);
                };

                // Handle initial data
                eventSource.addEventListener('init', function(event) {
                    const data = JSON.parse(event.data);
                    console.log('Received initial data:', data);

                    // Process articles
                    processArticles(data.articles);

                    // Update sources and trust scores
                    updateData(data);
                });

                // Handle updates
                eventSource.addEventListener('update', function(event) {
                    const data = JSON.parse(event.data);
                    console.log('Received update:', data);

                    // Process new articles
                    processArticles(data.articles);

                    // Update sources and trust scores
                    updateData(data);
                });
            }
        </script>
    </body>
    </html>
    """

# Run the server
if __name__ == "__main__":
    logger.info(f"Starting real-time dashboard on {HOST}:{PORT}")
    logger.info(f"Dashboard will be available at http://{HOST}:{PORT}")

    try:
        uvicorn.run(app, host=HOST, port=PORT, log_level="info")
    except Exception as e:
        logger.error(f"Error starting real-time dashboard: {str(e)}")
