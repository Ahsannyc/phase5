# Docker Image Contracts

**Date**: 2026-02-08
**Feature**: 001-cloud-native-deploy
**Purpose**: Specify expected Docker image structure, tagging, and registry locations

---

## Frontend Image Contract

**Name**: todo-frontend
**Tag**: latest (local development), semver for production (future)
**Registry**: localhost (local Docker daemon - Minikube)
**Base Image**: nginx:alpine (runtime stage)
**Builder Image**: node:20-alpine

### Structure

```dockerfile
# Stage 1: Builder
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json pnpm-lock.yaml .
RUN pnpm install --frozen-lockfile
COPY . .
RUN pnpm build

# Stage 2: Runtime
FROM nginx:alpine
COPY --from=builder /app/.next/standalone /usr/share/nginx/html
COPY --from=builder /app/public /usr/share/nginx/html/public
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
HEALTHCHECK CMD curl --fail http://localhost:80 || exit 1
```

### Size & Performance Goals

- **Final image size**: <150MB
- **Build time**: <5 minutes (pnpm cache used)
- **Startup time**: <5 seconds
- **Memory at runtime**: <100MB

### Expected Contents

- nginx binary (serving port 80)
- .next/standalone output (Next.js app)
- public/ directory (static assets)
- No node_modules, no dev dependencies

### Health Check

- **Endpoint**: HTTP GET to http://localhost:80
- **Expected response**: 200 OK (nginx default)
- **Initial delay**: 5 seconds (nginx startup)
- **Timeout**: 2 seconds

### Environment Variables

None required in Dockerfile; frontend config via:
- NEXT_PUBLIC_OPENAI_DOMAIN_KEY (optional, ChatKit domain)
- API base URL (hardcoded in frontend or via config)

### Non-Root User

- **User**: nginx (default in nginx:alpine)
- **UID**: 101
- **GID**: 101

---

## Backend Image Contract

**Name**: todo-backend
**Tag**: latest (local development), semver for production (future)
**Registry**: localhost (local Docker daemon - Minikube)
**Base Image**: python:3.11-slim (both builder and runtime)

### Structure

```dockerfile
# Stage 1: Builder
FROM python:3.11-slim AS builder
WORKDIR /app
COPY pyproject.toml poetry.lock .
RUN pip install poetry && poetry export -f requirements.txt | pip install -r /dev/stdin
RUN mkdir /app/venv && pip install --target /app/venv -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /app/venv /app/venv
COPY . .
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser
EXPOSE 8000
ENV PATH="/app/venv/bin:$PATH"
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
HEALTHCHECK CMD curl --fail http://localhost:8000/health || exit 1
```

### Size & Performance Goals

- **Final image size**: <300MB
- **Build time**: <3 minutes (virtualenv copy from builder)
- **Startup time**: <10 seconds
- **Memory at runtime**: <200MB

### Expected Contents

- python3.11 binary
- virtualenv with FastAPI, SQLModel, Alembic, OpenAI Agents SDK, Cohere API, etc.
- app/ directory (application code)
- No dev dependencies (pytest, black, etc.) in runtime

### Health Check

- **Endpoint**: HTTP GET to http://localhost:8000/health
- **Expected response**: 200 OK (application must provide endpoint)
- **Initial delay**: 30 seconds (app startup, DB connection)
- **Timeout**: 2 seconds

### Environment Variables at Runtime

- **DATABASE_URL**: Injected from Kubernetes Secret (local: from .env)
- **BETTER_AUTH_SECRET**: Injected from Kubernetes Secret (local: from .env)
- **COHERE_API_KEY**: Injected from Kubernetes Secret (local: from .env)
- **OPENAI_API_KEY**: Injected from Kubernetes Secret (local: from .env)

### Non-Root User

- **User**: appuser
- **UID**: 1000
- **GID**: 1000

---

## Image Building

### docker-compose up

```bash
# Auto-builds both images with docker-compose build
docker-compose up --build

# Images tagged as:
# - todo_frontend:latest (from docker-compose.yml service name)
# - todo_backend:latest (from docker-compose.yml service name)
```

### docker buildx (manual, if needed)

```bash
# Frontend
docker buildx build -t todo-frontend:latest -f docker/frontend.Dockerfile .

# Backend
docker buildx build -t todo-backend:latest -f docker/backend.Dockerfile .
```

### Minikube Local Images

```bash
# Set Docker context to Minikube
eval $(minikube docker-env)

# Build images directly into Minikube Docker daemon
docker-compose build
# or
docker build -t todo-frontend:latest -f docker/frontend.Dockerfile .
docker build -t todo-backend:latest -f docker/backend.Dockerfile .

# Verify images in Minikube
docker images | grep todo
```

---

## Image Registry & Pulling

- **Local development**: Images built and stored in local Docker daemon
- **Minikube**: Images must be built in Minikube's Docker daemon (use `eval $(minikube docker-env)`)
- **imagePullPolicy**: IfNotPresent (Helm default) - will use local if available
- **imagePullSecrets**: None required (no external registry)

---

## Image Security

- Multi-stage builds: dev dependencies not shipped to runtime
- Non-root user: both images run as non-root (nginx, appuser)
- No hardcoded secrets: env vars injected at runtime
- Minimal base images: alpine (frontend), python:3.11-slim (backend)

---

## Image Validation

After building, validate:

```bash
# Check image size
docker images | grep todo
# Expected: <150MB (frontend), <300MB (backend)

# Check non-root user
docker run --rm todo-frontend whoami
# Expected: nginx (or UID 101)

docker run --rm todo-backend whoami
# Expected: appuser (or UID 1000)

# Check health check command
docker inspect todo-frontend | grep -A 5 HealthCheck
# Expected: curl --fail http://localhost:80

docker inspect todo-backend | grep -A 5 HealthCheck
# Expected: curl --fail http://localhost:8000/health

# Check exposed ports
docker inspect todo-frontend | grep -E '"ExposedPorts"'
# Expected: "80/tcp"

docker inspect todo-backend | grep -E '"ExposedPorts"'
# Expected: "8000/tcp"
```

---

## .dockerignore Contract

Both Dockerfiles reference .dockerignore in project root:

```
# Build artifacts
node_modules
.next/cache
.next/build
dist
build
__pycache__
.venv
venv

# Git & version control
.git
.gitignore
.gitmodules

# Dependencies
.yarn
.pnpm-store

# Environment files (never include)
.env
.env.local
.env.*.local

# IDE & OS files
.vscode
.idea
*.swp
*.swo
.DS_Store
Thumbs.db

# Tests & coverage (not needed in production image)
.pytest_cache
.coverage
htmlcov

# Docker files themselves
Dockerfile
docker-compose.yml
.dockerignore
```

This ensures images don't contain unnecessary files and have minimal size.
