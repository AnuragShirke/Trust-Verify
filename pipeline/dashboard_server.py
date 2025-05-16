#!/usr/bin/env python
"""
Real-Time Dashboard Server

This script provides a FastAPI server with WebSocket support for real-time updates.
"""

import os
import json
import time
import logging
import datetime
import asyncio
import redis
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from typing import List, Dict, Any, Set

# Configure logging
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/dashboard_server.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("dashboard_server")

# Redis configuration
REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
REDIS_DB = int(os.environ.get("REDIS_DB", 0))
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD", None)
REDIS_STREAM_NAME = os.environ.get("REDIS_STREAM_NAME", "news_articles")

# Server configuration
# Always bind to all interfaces
HOST = "0.0.0.0"
PORT = int(os.environ.get("PORT", 8080))

# Create the FastAPI app
app = FastAPI(title="Fake News Detector Dashboard")

# Add simple test endpoints
@app.get("/ping")
async def ping():
    return {"status": "ok", "message": "Dashboard server is running"}

@app.get("/test")
async def test():
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Page</title>
    </head>
    <body>
        <h1>Test Page</h1>
        <p>If you can see this, the dashboard server is working correctly.</p>
    </body>
    </html>
    """)

# Create a connection pool for Redis
redis_pool = redis.ConnectionPool(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    password=REDIS_PASSWORD,
    decode_responses=True
)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"WebSocket client connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"WebSocket client disconnected. Total connections: {len(self.active_connections)}")

    async def broadcast(self, message: str):
        disconnected = set()
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error sending message to WebSocket: {str(e)}")
                disconnected.add(connection)

        # Remove disconnected clients
        for connection in disconnected:
            self.disconnect(connection)

manager = ConnectionManager()

# Redis listener task
async def redis_listener():
    """Listen for new messages in the Redis stream and broadcast them to WebSocket clients."""
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

                        # Broadcast the message to all WebSocket clients
                        await manager.broadcast(json.dumps({
                            "id": message_id,
                            "data": message_data
                        }))
        except Exception as e:
            logger.error(f"Error in Redis listener: {str(e)}")
            await asyncio.sleep(5)  # Wait before retrying

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Just keep the connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        manager.disconnect(websocket)

# HTML for the dashboard
@app.get("/", response_class=HTMLResponse)
async def get_dashboard():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Fake News Detector - Real-Time Dashboard</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .container {
                max-width: 800px;
                margin: 0 auto;
                background-color: white;
                padding: 20px;
                border-radius: 5px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            h1 {
                color: #333;
            }
            .status {
                margin-top: 20px;
                padding: 10px;
                background-color: #e6f7ff;
                border: 1px solid #91d5ff;
                border-radius: 5px;
            }
            .button {
                display: inline-block;
                margin-top: 20px;
                padding: 10px 20px;
                background-color: #1890ff;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
            }
            .button:hover {
                background-color: #40a9ff;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Fake News Detector Dashboard</h1>
            <p>Welcome to the real-time dashboard for the Fake News Detector pipeline.</p>

            <div class="status">
                <p><strong>Server Status:</strong> Running</p>
                <p><strong>WebSocket Status:</strong> <span id="ws-status">Checking...</span></p>
            </div>

            <button class="button" onclick="testWebSocket()">Test WebSocket Connection</button>

            <div id="result" style="margin-top: 20px;"></div>
        </div>

        <script>
            // Simple WebSocket test
            function testWebSocket() {
                const resultDiv = document.getElementById('result');
                const statusSpan = document.getElementById('ws-status');

                resultDiv.innerHTML = "Testing WebSocket connection...";
                statusSpan.innerHTML = "Connecting...";

                const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                const wsUrl = `${wsProtocol}//${window.location.host}/ws`;

                try {
                    const ws = new WebSocket(wsUrl);

                    ws.onopen = function() {
                        console.log("WebSocket connection established");
                        resultDiv.innerHTML = "WebSocket connection successful!";
                        statusSpan.innerHTML = "Connected";
                        statusSpan.style.color = "green";
                    };

                    ws.onclose = function() {
                        console.log("WebSocket connection closed");
                        resultDiv.innerHTML = "WebSocket connection closed.";
                        statusSpan.innerHTML = "Disconnected";
                        statusSpan.style.color = "red";
                    };

                    ws.onerror = function(error) {
                        console.error("WebSocket error:", error);
                        resultDiv.innerHTML = "Error connecting to WebSocket. Check console for details.";
                        statusSpan.innerHTML = "Error";
                        statusSpan.style.color = "red";
                    };
                } catch (error) {
                    console.error("Error creating WebSocket:", error);
                    resultDiv.innerHTML = "Error creating WebSocket: " + error.message;
                    statusSpan.innerHTML = "Error";
                    statusSpan.style.color = "red";
                }
            }
        </script>
    </body>
    </html>
    """

# Suppress the deprecation warning
import warnings
warnings.filterwarnings("ignore", message="on_event is deprecated")

# Startup event to start the Redis listener
@app.on_event("startup")
async def startup_event():
    # Start the Redis listener in the background
    asyncio.create_task(redis_listener())
    logger.info("Dashboard server started")

# Shutdown event to clean up resources
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Dashboard server shutting down")

# Run the server
if __name__ == "__main__":
    logger.info(f"Starting dashboard server on {HOST}:{PORT}")
    logger.info(f"Dashboard will be available at http://{HOST}:{PORT}")
    logger.info(f"WebSocket will be available at ws://{HOST}:{PORT}/ws")
    try:
        # Be more explicit with the configuration
        config = uvicorn.Config(
            app=app,
            host=HOST,
            port=PORT,
            log_level="info",
            access_log=True,
            interface="asgi3",
            reload=False
        )
        server = uvicorn.Server(config)
        server.run()
    except Exception as e:
        logger.error(f"Error starting dashboard server: {str(e)}")
