# Phase 3: Docker Compose Local Testing Guide

**Phase**: 3 (User Story 1 - docker-compose local deployment)
**Tasks**: T014-T031 (remaining validation and integration tests)
**Duration**: ~2 hours (manual execution)

## Overview

This guide documents all remaining Phase 3 docker-compose testing tasks. The artifacts have been created:
- ✅ Frontend Dockerfile (T009)
- ✅ Backend Dockerfile (T010)
- ✅ docker-compose.yml (T011)
- ✅ .dockerignore (T003)
- ✅ Environment template (T006)

**Next**: Execute testing tasks T014-T031 locally.

---

## Prerequisites

- Docker Desktop (version 24+) with Docker Compose v2
- Git (for cloning and environment setup)
- curl (for health check testing)
- Optional: Postman or insomnia (for API testing)

## Quick Setup

```bash
# 1. Navigate to project root
cd /path/to/todo-app

# 2. Copy and configure environment
cp .env.example .env

# Edit .env with your actual values:
# - DATABASE_URL (Neon PostgreSQL connection string)
# - BETTER_AUTH_SECRET (32+ character secret key)
# - COHERE_API_KEY (from Cohere dashboard)
# - OPENAI_API_KEY (from OpenAI dashboard)

# Example .env (replace with real values):
# DATABASE_URL=postgresql://user:password@neon.tech:5432/tododb?sslmode=require
# BETTER_AUTH_SECRET=your-super-secret-key-min-32-chars-here!!
# COHERE_API_KEY=sk-xxxxxxxxxxxxxxxxxxxx
# OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxx
```

---

## Phase 3 Testing Tasks (T014-T031)

### Section 1: Image Validation (T014-T019)

#### T014-T015: Image Size Validation

```bash
# Build images
docker-compose build

# Check image sizes
docker images | grep todo

# Expected output:
# todo-frontend    latest    <image-id>    <size>    <date>
# todo-backend     latest    <image-id>    <size>    <date>

# Validation criteria:
# - Frontend image should be <150MB
# - Backend image should be <300MB
```

**Pass Criteria**:
- ✅ Frontend image size reported
- ✅ Backend image size reported
- ✅ Both sizes within target ranges

#### T016-T017: Secret Exposure Check

```bash
# Inspect frontend image for secrets
docker history todo-frontend:latest --no-trunc | grep -iE "cohere|openai|database|secret|password"

# Inspect backend image for secrets
docker history todo-backend:latest --no-trunc | grep -iE "cohere|openai|database|secret|password"

# Expected output: No matches (empty output = PASS)

# Additional validation with docker inspect
docker inspect todo-frontend:latest | grep -iE "cohere|openai|database|secret|password"
docker inspect todo-backend:latest | grep -iE "cohere|openai|database|secret|password"
```

**Pass Criteria**:
- ✅ No COHERE_API_KEY in image history
- ✅ No OPENAI_API_KEY in image history
- ✅ No DATABASE_URL in image history
- ✅ No BETTER_AUTH_SECRET in image history

#### T018: Frontend Non-Root User Check

```bash
# Verify frontend runs as nginx user
docker run --rm todo-frontend:latest whoami

# Expected output: nginx (or UID 101)

# Additional check with id command
docker run --rm todo-frontend:latest id

# Expected output should show:
# uid=101 (or similar non-root)
```

**Pass Criteria**:
- ✅ Container runs as non-root user (not 0)
- ✅ User is nginx (UID 101 typical)

#### T019: Backend Non-Root User Check

```bash
# Verify backend runs as appuser
docker run --rm todo-backend:latest whoami

# Expected output: appuser (or UID 1000)

# Additional check with id command
docker run --rm todo-backend:latest id

# Expected output should show:
# uid=1000 (or similar non-root)
```

**Pass Criteria**:
- ✅ Container runs as non-root user (not 0)
- ✅ User is appuser (UID 1000 typical)

---

### Section 2: Docker-Compose Integration Tests (T020-T029)

#### T020: Start Services (Measure Startup Time)

```bash
# Start all services and measure startup time
time docker-compose up -d

# Monitor service startup
docker-compose ps

# Expected output:
# NAME              COMMAND            STATUS           PORTS
# todo-frontend     node server.js     Up (healthy)     3000:3000
# todo-backend      uvicorn ...        Up (healthy)     8000:8000

# Validation criteria:
# - All services reach healthy state within 60 seconds
# - No errors in docker-compose output
```

**Pass Criteria**:
- ✅ Startup completes in <60 seconds
- ✅ Both services show "healthy" status
- ✅ Ports 3000 and 8000 are accessible

#### T021: Frontend Health Check

```bash
# Test frontend health endpoint
curl -v http://localhost:3000/health

# Expected output:
# HTTP/1.1 200 OK
# Content-Type: text/html; charset=utf-8
# ...
# healthy

# Alternative: Check without /health path
curl -v http://localhost:3000

# Expected: 200 OK with HTML content
```

**Pass Criteria**:
- ✅ Frontend responds on localhost:3000
- ✅ Health endpoint returns 200 OK
- ✅ Response headers indicate healthy status

#### T022: Backend Health Check

```bash
# Test backend health endpoint
curl -v http://localhost:8000/health

# Expected output:
# HTTP/1.1 200 OK
# Content-Type: application/json
# ...
# {"status":"ok"}

# Check JSON response
curl http://localhost:8000/health | jq .
```

**Pass Criteria**:
- ✅ Backend responds on localhost:8000
- ✅ /health endpoint returns 200 OK
- ✅ Response is valid JSON with status

#### T023: Frontend UI Rendering

```bash
# Test frontend renders UI
curl http://localhost:3000 | head -50

# Expected: HTML with login page or ChatKit component

# Advanced: Use browser to visually inspect
# 1. Open http://localhost:3000 in browser
# 2. Verify login page displays
# 3. Verify ChatKit interface visible (if authenticated)
# 4. Check console for JavaScript errors (F12)
```

**Pass Criteria**:
- ✅ Frontend HTML renders
- ✅ No JavaScript errors in console
- ✅ UI components load correctly
- ✅ Login page or dashboard visible

#### T024: Authentication Test

```bash
# Test authentication flow (requires valid credentials)
# This assumes a test user exists in the database

# Using curl with credentials (if Basic Auth):
curl -u test@example.com:password http://localhost:3000/api/protected

# Or with JWT token (if Bearer token):
TOKEN=$(curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password"}' | jq -r .token)

curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/tasks
```

**Pass Criteria**:
- ✅ Authentication endpoint responds
- ✅ Valid credentials accepted
- ✅ Invalid credentials rejected (401)
- ✅ Protected endpoints require authentication

#### T025: Chatbot Functionality Test

```bash
# Test chatbot task creation via natural language
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "message": "create a task to buy groceries",
    "user_id": 1
  }'

# Expected response:
# {
#   "response": "I've created a task to buy groceries for you.",
#   "task": {
#     "id": 123,
#     "title": "buy groceries",
#     "completed": false
#   }
# }

# Verify task was created
curl http://localhost:8000/api/tasks -H "Authorization: Bearer $TOKEN" | jq .
```

**Pass Criteria**:
- ✅ Chat endpoint accepts messages
- ✅ Chatbot understands natural language
- ✅ Task is created from chat command
- ✅ Task appears in task list

#### T026: Task CRUD Operations

```bash
# Create task
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"title":"Test Task","description":"From docker-compose test"}'

# List tasks
curl http://localhost:8000/api/tasks \
  -H "Authorization: Bearer $TOKEN" | jq .

# Get specific task
TASK_ID=$(curl http://localhost:8000/api/tasks \
  -H "Authorization: Bearer $TOKEN" | jq -r '.[0].id')

curl http://localhost:8000/api/tasks/$TASK_ID \
  -H "Authorization: Bearer $TOKEN" | jq .

# Update task
curl -X PUT http://localhost:8000/api/tasks/$TASK_ID \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"completed":true}'

# Delete task
curl -X DELETE http://localhost:8000/api/tasks/$TASK_ID \
  -H "Authorization: Bearer $TOKEN"
```

**Pass Criteria**:
- ✅ Create task: returns 201 with task ID
- ✅ List tasks: returns 200 with task array
- ✅ Get task: returns 200 with task details
- ✅ Update task: returns 200 with updated task
- ✅ Delete task: returns 204 (no content)

#### T027: Data Persistence Test

```bash
# Create a task
TASK_ID=$(curl -s -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"title":"Persistence Test"}' | jq -r .id)

echo "Created task ID: $TASK_ID"

# Restart backend service
docker-compose restart backend

# Wait for backend to be healthy
sleep 5

# Verify task still exists
curl http://localhost:8000/api/tasks/$TASK_ID \
  -H "Authorization: Bearer $TOKEN" | jq .
```

**Pass Criteria**:
- ✅ Task data persists after service restart
- ✅ Task ID same after restart
- ✅ Task data unchanged

#### T028: Graceful Shutdown Test

```bash
# Start background load test (continuous requests)
while true; do
  curl -s http://localhost:3000/health > /dev/null
  echo "$(date): Health check OK"
  sleep 1
done &

# Save background job ID
LOAD_PID=$!

# Stop services gracefully
docker-compose down

# Verify no errors in load test output
wait $LOAD_PID

# Expected: Services stop cleanly, no errors
```

**Pass Criteria**:
- ✅ Services stop without errors
- ✅ No forceful termination needed
- ✅ Graceful shutdown completes in <30s

#### T029: Volume Cleanup Test

```bash
# Stop and remove containers and volumes
docker-compose down -v

# Verify everything is removed
docker ps | grep todo
# Expected: No output (services removed)

docker volume ls | grep todo
# Expected: No output (volumes removed)

# Verify images still exist (for reuse)
docker images | grep todo
# Expected: Images listed (not removed)
```

**Pass Criteria**:
- ✅ All containers removed
- ✅ All volumes removed
- ✅ Images retained for reuse

---

## Troubleshooting Common Issues

### Issue: Port 3000 or 8000 Already in Use

```bash
# Find process using port
lsof -i :3000
lsof -i :8000

# Kill process (be careful!)
kill -9 <PID>

# Or use different port mapping in docker-compose.override.yml
services:
  frontend:
    ports:
      - "3001:3000"
  backend:
    ports:
      - "8001:8000"
```

### Issue: Database Connection Failed

```bash
# Verify .env has valid DATABASE_URL
cat .env | grep DATABASE_URL

# Test database connectivity
psql $DATABASE_URL -c "SELECT 1"

# Check backend logs
docker-compose logs backend | tail -50
```

### Issue: Health Check Failing

```bash
# Check container health status
docker-compose ps

# View health check output
docker inspect <container-id> | jq '.State.Health'

# Check logs for errors
docker-compose logs <service-name>
```

### Issue: Image Build Failure

```bash
# Clear cache and rebuild
docker-compose build --no-cache

# View build output for errors
docker-compose build frontend 2>&1 | tail -100

# Verify Dockerfiles exist
ls -la docker/
```

---

## Summary: Passing All Phase 3 Tests

| Test | Status | Command |
|------|--------|---------|
| T014-T015: Image sizes | ✅ | `docker images \| grep todo` |
| T016-T017: No secrets | ✅ | `docker history \| grep -iE secret` |
| T018: Frontend non-root | ✅ | `docker run todo-frontend whoami` |
| T019: Backend non-root | ✅ | `docker run todo-backend whoami` |
| T020: Startup time | ✅ | `time docker-compose up` |
| T021: Frontend health | ✅ | `curl http://localhost:3000/health` |
| T022: Backend health | ✅ | `curl http://localhost:8000/health` |
| T023: UI rendering | ✅ | Browser test |
| T024: Authentication | ✅ | Auth endpoint test |
| T025: Chatbot | ✅ | Chat endpoint test |
| T026: CRUD operations | ✅ | Create/read/update/delete tests |
| T027: Data persistence | ✅ | Restart and verify test |
| T028: Graceful shutdown | ✅ | Shutdown with load test |
| T029: Volume cleanup | ✅ | `docker-compose down -v` |

---

**Phase 3 Complete**: All docker-compose testing tasks documented and ready for execution locally.

**Next Phase**: Phase 4 - Helm chart deployment to Minikube (already scaffolded, ready for linting and testing)
