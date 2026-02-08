# Multi-stage Dockerfile for FastAPI backend
# Stage 1: Builder - Python with poetry/pip
# Stage 2: Runtime - Python running uvicorn

# ===========================
# Stage 1: Builder
# ===========================
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements files
COPY backend/requirements.txt ./requirements.txt

# Create virtual environment and install dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ===========================
# Stage 2: Runtime
# ===========================
FROM python:3.11-slim

LABEL maintainer="Todo App Team"
LABEL description="Todo App Backend - FastAPI with uvicorn"

# Install curl for health checks
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for app
RUN groupadd -g 1000 app && \
    useradd -u 1000 -g app -d /app -s /sbin/nologin -c "App user" app

# Set working directory
WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder --chown=app:app /opt/venv /opt/venv

# Copy application source code
COPY --chown=app:app backend/ .

# Set environment variables
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Expose port 8000
EXPOSE 8000

# Run as non-root user
USER app

# Health check instruction
# Checks if FastAPI server is responding on /health endpoint
HEALTHCHECK --interval=10s --timeout=2s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start FastAPI application with uvicorn
# - host 0.0.0.0: listen on all interfaces
# - port 8000: default port
# - workers 4: multiple workers for concurrency
# - no-access-log: reduce log verbosity
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
