# ============================================================================
# Multi-stage Dockerfile for Next.js Frontend
# Optimized for production with security hardening and minimal image size
# Target: <100MB final image
# ============================================================================

# ============================================================================
# Stage 1: Dependencies - Install node modules
# ============================================================================
FROM node:20-alpine AS deps

# Install libc6-compat for Node.js compatibility on Alpine
RUN apk add --no-cache libc6-compat

WORKDIR /app

# Copy package files for dependency installation
COPY frontend/package.json frontend/package-lock.json* ./

# Install dependencies
# Use npm install for flexibility with lock file mismatches during development
# In production CI/CD, use npm ci with properly synced lock file
RUN npm install --omit=dev --frozen-lockfile || npm install --omit=dev

# ============================================================================
# Stage 2: Builder - Build Next.js application
# ============================================================================
FROM node:20-alpine AS builder

WORKDIR /app

# Copy dependencies from deps stage
COPY --from=deps /app/node_modules ./node_modules

# Copy all source files
COPY frontend/ .

# Set environment variable for Next.js standalone output
ENV NEXT_TELEMETRY_DISABLED=1 \
    NODE_ENV=production

# Build Next.js application
# Next.js will automatically create standalone output if configured
RUN npm run build

# ============================================================================
# Stage 3: Runtime - Minimal production image
# ============================================================================
FROM node:20-alpine AS runner

# Metadata labels
LABEL maintainer="Todo App Team" \
      description="Production-ready Next.js frontend with multi-stage build" \
      version="1.0.0" \
      org.opencontainers.image.source="https://github.com/your-org/todo-app"

# Install only curl for health checks (minimal runtime dependencies)
RUN apk add --no-cache curl

# Create non-root user for security
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

WORKDIR /app

# Set production environment
ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1

# Copy built application artifacts
# For standalone build: .next/standalone contains the minimal server
# For static build: copy .next directory
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static
COPY --from=builder --chown=nextjs:nodejs /app/public ./public

# Expose application port
EXPOSE 3000

# Set port environment variable
ENV PORT=3000 \
    HOSTNAME="0.0.0.0"

# Switch to non-root user (security best practice)
USER nextjs

# Health check for Kubernetes liveness/readiness probes
# Checks every 30s, timeout 10s, start after 40s, max 3 retries
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:3000/api/health || curl -f http://localhost:3000 || exit 1

# Start Next.js standalone server
CMD ["node", "server.js"]
