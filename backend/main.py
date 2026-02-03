"""
Accident Incident Responder - Main Application
FastAPI Backend with WebSocket support
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import logging
import os
import json
from typing import List

from config import get_settings
from database import init_db
from routers import incidents, cameras, dispatch

settings = get_settings()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Failed to send message: {e}")


manager = ConnectionManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting Accident Incident Responder...")
    init_db()
    
    # Create required directories
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.REPORTS_DIR, exist_ok=True)
    os.makedirs(settings.SNAPSHOTS_DIR, exist_ok=True)
    
    logger.info("Database initialized. Directories created.")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Accident Incident Responder...")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="ML-based Accident Incident Responder with Police & Ambulance Integration",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(incidents.router, prefix=settings.API_V1_PREFIX)
app.include_router(cameras.router, prefix=settings.API_V1_PREFIX)
app.include_router(dispatch.router, prefix=settings.API_V1_PREFIX)


# Static files for uploads/reports (if directories exist)
if os.path.exists(settings.UPLOAD_DIR):
    app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")
if os.path.exists(settings.REPORTS_DIR):
    app.mount("/reports", StaticFiles(directory=settings.REPORTS_DIR), name="reports")
if os.path.exists(settings.SNAPSHOTS_DIR):
    app.mount("/snapshots", StaticFiles(directory=settings.SNAPSHOTS_DIR), name="snapshots")


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "name": settings.APP_NAME,
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "api": settings.API_V1_PREFIX
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time incident updates.
    Dashboard connects here to receive:
    - New incident alerts
    - Status updates
    - Dispatch notifications
    """
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle ping/pong
            if message.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
            
            # Handle subscription to specific incident
            elif message.get("type") == "subscribe":
                incident_id = message.get("incident_id")
                await websocket.send_json({
                    "type": "subscribed",
                    "incident_id": incident_id
                })
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# Function to broadcast new incidents (called from incident creation)
async def broadcast_new_incident(incident_data: dict):
    """Broadcast new incident to all connected dashboards"""
    await manager.broadcast({
        "type": "new_incident",
        "data": incident_data
    })


async def broadcast_status_update(incident_id: str, status: str):
    """Broadcast incident status update"""
    await manager.broadcast({
        "type": "status_update",
        "incident_id": incident_id,
        "status": status
    })


async def broadcast_alert(severity: str, message: str):
    """Broadcast critical alert"""
    await manager.broadcast({
        "type": "alert",
        "severity": severity,
        "message": message
    })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
