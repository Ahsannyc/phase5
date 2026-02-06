"""Main FastAPI application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.auth import auth_router
from app.api.tasks import tasks_router
from app.core.config import settings


# Create FastAPI app instance
app = FastAPI(
    title="Todo API",
    description="A secure, scalable backend for the multi-user Todo web application",
    version="1.0.0"
)


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.better_auth_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include API routers
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(tasks_router, prefix="/api/tasks", tags=["tasks"])


@app.get("/")
def read_root():
    """Root endpoint."""
    return {"message": "Todo API is running!"}


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}