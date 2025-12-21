"""Main FastAPI application for Numa - Protocolo Nexus Edition.

This is the unified entry point for the modular monolith.
Run with: python src/main.py
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.database import Base, engine
from src.core.config import settings
from src.modules.api_gateway.router import router

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="The most intuitive financial assistant that organizes your finances through conversation, without compromising your privacy. Built with Protocolo Nexus.",
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Gateway router
app.include_router(router, prefix="/api", tags=["Numa API"])

# Root endpoint (outside /api prefix)
@app.get("/")
def root():
    """Root endpoint."""
    return {
        "message": "Welcome to Numa AI - Protocolo Nexus Edition",
        "version": settings.APP_VERSION,
        "architecture": "Modular Monolith",
        "docs": "/docs",
        "api": "/api"
    }


if __name__ == "__main__":
    # Run the application
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )
