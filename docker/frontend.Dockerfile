# Multi-stage Dockerfile for Next.js frontend
# Stage 1: Builder - Node.js with pnpm
# Stage 2: Runtime - Node.js running Next.js standalone server

# ===========================
# Stage 1: Builder
# ===========================
FROM node:20-alpine AS builder

WORKDIR /app

# Install pnpm (faster than npm)
RUN npm install -g pnpm

# Copy dependency files
COPY frontend/package.json frontend/pnpm-lock.yaml ./

# Install dependencies with frozen lockfile (reproducible builds)
RUN pnpm install --frozen-lockfile

# Copy application source code
COPY frontend/ .

# Build Next.js application to standalone output
RUN pnpm build

# ===========================
# Stage 2: Runtime
# ===========================
FROM node:20-alpine

LABEL maintainer="Todo App Team"
LABEL description="Todo App Frontend - Next.js Standalone Server"

# Install curl for health checks
RUN apk add --no-cache curl

# Create non-root user for app
RUN addgroup -g 1000 -S app && \
    adduser -S -D -H -u 1000 -h /app -s /sbin/nologin -G app -g app app

# Set working directory
WORKDIR /app

# Copy built application from builder stage
COPY --from=builder --chown=app:app /app/.next/standalone ./
COPY --from=builder --chown=app:app /app/public ./public

# Copy package.json for reference (not needed for standalone, but kept for clarity)
COPY --chown=app:app frontend/package.json ./

# Expose port 3000 (mapped to 80 at docker-compose level)
EXPOSE 3000

# Run as non-root user
USER app

# Health check instruction
# Checks if Next.js server is responding
HEALTHCHECK --interval=10s --timeout=2s --retries=3 \
    CMD curl -f http://localhost:3000 || exit 1

# Start Next.js standalone server
# The standalone build includes server.js entry point
CMD ["node", "server.js"]
