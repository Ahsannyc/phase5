# ============================================================================
# Multi-stage Dockerfile for FastAPI Backend
# Optimized for production with security hardening and minimal image size
# Target: <200MB final image
# ============================================================================

# ============================================================================
# Stage 1: Build Stage - Compile dependencies
# ============================================================================
FROM python:3.11-slim AS builder

# Set working directory
WORKDIR /app

# Install build dependencies for compiling Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements file first (layer caching optimization)
COPY backend/requirements.txt .

# Create virtual environment and install dependencies
# Using venv for isolation and easy copying to runtime stage
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies with optimizations
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ============================================================================
# Stage 2: Runtime Stage - Minimal production image
# ============================================================================
FROM python:3.11-slim

# Metadata labels
LABEL maintainer="Todo App Team" \
      description="Production-ready FastAPI backend with multi-stage build" \
      version="1.0.0" \
      org.opencontainers.image.source="https://github.com/your-org/todo-app"

# Install runtime dependencies only (minimal set)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security (uid 1000 for consistency)
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app && \
    chown -R appuser:appuser /app

# Set working directory
WORKDIR /app

# Copy virtual environment from builder stage
COPY --from=builder --chown=appuser:appuser /opt/venv /opt/venv

# Copy application source code (only app directory, not tests)
COPY --chown=appuser:appuser backend/app ./app

# Set environment variables for production
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

# Expose application port
EXPOSE 8000

# Switch to non-root user (security best practice)
USER appuser

# Health check for Kubernetes liveness/readiness probes
# Checks every 30s, timeout 10s, start after 40s, max 3 retries
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run FastAPI application with uvicorn
# Production settings: single worker for container (K8s handles scaling)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
