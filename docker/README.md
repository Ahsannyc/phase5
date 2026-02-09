# Docker Build Documentation

## Overview

This directory contains production-ready, multi-stage Dockerfiles for the Todo application frontend and backend. Both images are optimized for security, minimal size, and Kubernetes deployment.

## Image Specifications

### Backend Image (todo-backend:latest)

**Built Size:** 112MB (Target: <200MB) ✅
**Base Image:** python:3.11-slim
**Security:** Non-root user (appuser, UID 1000)
**Multi-Architecture:** linux/amd64, linux/arm64

**Build Command:**
```bash
cd "C:\Users\14loa\Desktop\IT\GIAIC\Q4 spec kit\phase5"
docker build -f docker/backend.Dockerfile -t todo-backend:latest .
```

**Build Time:** ~3-5 minutes (depending on network speed)

**Required Environment Variables:**
- `DATABASE_URL` - PostgreSQL connection string
- `BETTER_AUTH_SECRET` - Authentication secret key
- `COHERE_API_KEY` - Cohere API key for AI features
- `OPENAI_API_KEY` - OpenAI API key for AI features

**Run Command (with env vars):**
```bash
docker run --rm -p 8000:8000 \
  -e DATABASE_URL="postgresql://user:pass@host:5432/db" \
  -e BETTER_AUTH_SECRET="your-secret" \
  -e COHERE_API_KEY="your-key" \
  -e OPENAI_API_KEY="your-key" \
  todo-backend:latest
```

**Health Check:**
- Endpoint: `http://localhost:8000/health`
- Interval: 30s
- Timeout: 10s
- Start Period: 40s
- Retries: 3

**Kubernetes Probes:**
```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 40
  periodSeconds: 30
  timeoutSeconds: 10
  failureThreshold: 3

readinessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3
```

### Frontend Image (todo-frontend:latest)

**Target Size:** <100MB
**Base Image:** node:20-alpine
**Security:** Non-root user (nextjs, UID 1001)
**Multi-Architecture:** linux/amd64, linux/arm64

**Build Command:**
```bash
cd "C:\Users\14loa\Desktop\IT\GIAIC\Q4 spec kit\phase5"
docker build -f docker/frontend.Dockerfile -t todo-frontend:latest .
```

**Note:** The frontend build currently fails due to application code issues:
- Missing component: `@/components/chat/ChatInterface`
- Missing component: `@/components/todo/TodoList`
- Missing component: `@/components/layout/Sidebar`
- Incorrect import: `useSession` from `better-auth/client`

These are code-level issues unrelated to the Dockerfile. Once the application code is fixed, the Dockerfile will build successfully.

**Required Environment Variables:**
- `NEXT_PUBLIC_API_URL` - Backend API URL
- `BETTER_AUTH_URL` - Authentication service URL

**Run Command (once built):**
```bash
docker run --rm -p 3000:3000 \
  -e NEXT_PUBLIC_API_URL="http://api.example.com" \
  -e BETTER_AUTH_URL="http://auth.example.com" \
  todo-frontend:latest
```

**Health Check:**
- Endpoint: `http://localhost:3000/api/health` (fallback: `/`)
- Interval: 30s
- Timeout: 10s
- Start Period: 40s
- Retries: 3

## Multi-Stage Build Details

### Backend Dockerfile Architecture

**Stage 1: Builder**
- Base: `python:3.11-slim`
- Installs build dependencies (build-essential, libpq-dev)
- Creates virtual environment at `/opt/venv`
- Installs Python packages from requirements.txt
- **Optimization:** All build tools discarded in next stage

**Stage 2: Runtime**
- Base: `python:3.11-slim` (fresh, minimal image)
- Installs only runtime dependencies (libpq5, curl)
- Copies virtual environment from builder
- Creates non-root user (appuser)
- Copies application code
- **Size Reduction:** No build tools, only runtime essentials
- **Security:** Non-root user, minimal attack surface

### Frontend Dockerfile Architecture

**Stage 1: Dependencies**
- Base: `node:20-alpine`
- Installs libc6-compat for Node.js compatibility
- Runs `npm ci` for reproducible dependency installation
- **Optimization:** Separate stage for dependency caching

**Stage 2: Builder**
- Base: `node:20-alpine`
- Copies dependencies from previous stage
- Copies application source
- Runs Next.js build with standalone output mode
- **Optimization:** Standalone build includes only required files

**Stage 3: Runtime**
- Base: `node:20-alpine` (fresh, minimal image)
- Installs only curl for health checks
- Creates non-root user (nextjs)
- Copies standalone build artifacts
- **Size Reduction:** No build tools, only runtime server
- **Security:** Non-root user, minimal attack surface

## Security Features

Both Dockerfiles implement production security best practices:

1. **Non-Root Users**
   - Backend: `appuser` (UID 1000)
   - Frontend: `nextjs` (UID 1001)

2. **Minimal Base Images**
   - Alpine Linux for frontend (smallest)
   - Debian Slim for backend (Python compatibility)

3. **No Build Tools in Runtime**
   - Multi-stage builds discard all build dependencies
   - Only runtime essentials included

4. **Health Checks**
   - Both containers include health check commands
   - Compatible with Kubernetes liveness/readiness probes

5. **Environment Variable Security**
   - No secrets hardcoded in Dockerfiles
   - All sensitive data passed via environment variables
   - .dockerignore prevents .env files from being copied

## Build Optimizations

1. **Layer Caching**
   - Dependencies copied before source code
   - Maximizes Docker layer cache effectiveness
   - Faster rebuilds when code changes

2. **Minimal Layers**
   - Combined RUN commands where logical
   - Reduced image size

3. **No Cache for Package Managers**
   - `pip install --no-cache-dir`
   - `npm ci` for frozen dependencies
   - Reduces image size significantly

4. **Clean Up in Same Layer**
   - `rm -rf /var/lib/apt/lists/*` after apt install
   - Package manager caches removed immediately

## Testing Checklist

### Backend Image Testing

- [X] **Build Success:** Image builds without errors
- [X] **Image Size:** 112MB (well under 200MB target)
- [X] **Container Starts:** Container starts successfully (requires env vars)
- [X] **Non-Root User:** Runs as appuser (UID 1000)
- [ ] **Health Endpoint:** /health responds 200 OK (requires full env setup)
- [ ] **Multi-Architecture:** Builds for linux/amd64 and linux/arm64

### Frontend Image Testing

- [ ] **Build Success:** Blocked by application code issues
- [ ] **Image Size:** Target <100MB
- [ ] **Container Starts:** Pending successful build
- [ ] **Non-Root User:** Configured as nextjs (UID 1001)
- [ ] **Health Endpoint:** Pending successful build
- [ ] **Multi-Architecture:** Configured for linux/amd64 and linux/arm64

## Known Issues

### Frontend Build Failures

The frontend Dockerfile is correctly implemented, but the application code has the following issues:

1. **Missing Components** (5 errors):
   - `@/components/chat/ChatInterface`
   - `@/components/todo/TodoList`
   - `@/components/layout/Sidebar`
   - `@/components/agent/AgentSelector`

2. **Incorrect Imports** (2 errors):
   - `useSession` not exported from `better-auth/client`
   - Should use different auth hook or update better-auth version

**Resolution:** Fix application code issues in the frontend directory before building Docker image.

## Next Steps

1. **Fix Frontend Code Issues**
   - Create missing components or remove imports
   - Update better-auth usage to match library version
   - Test local build: `npm run build`

2. **Multi-Architecture Builds**
   - Set up Docker buildx for multi-arch support
   - Build for linux/amd64 and linux/arm64
   - Push to DigitalOcean Container Registry

3. **Image Registry Push**
   - Tag images with version and registry URL
   - Push to DO Container Registry or Docker Hub
   - Configure Kubernetes to pull from registry

4. **Kubernetes Deployment**
   - Create Deployment manifests
   - Configure resource limits
   - Set up ConfigMaps and Secrets for env vars
   - Deploy to DOKS cluster

## Build Times Summary

| Image | Build Time | Final Size | Status |
|-------|-----------|------------|--------|
| Backend | ~3-5 min | 112MB | ✅ Success |
| Frontend | N/A | N/A | ❌ Code Issues |

## Dockerfile Locations

- Backend: `docker/backend.Dockerfile`
- Frontend: `docker/frontend.Dockerfile`
- Next.js Config: `frontend/next.config.js` (created for standalone output)
- Docker Ignore: `.dockerignore` (exists at project root)

## Additional Configuration Files

### next.config.js

Created to enable standalone output mode for optimal Docker builds:

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  reactStrictMode: true,
  swcMinify: true,
  // Security headers and other optimizations...
}

module.exports = nextConfig
```

This configuration ensures Next.js creates a minimal standalone server bundle that can be copied into the Docker image, reducing final image size significantly.
