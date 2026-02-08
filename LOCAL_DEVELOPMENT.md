# Local Development Setup Guide

**Difficulty**: Beginner
**Time**: 15 minutes
**Prerequisites**: Git, Docker Desktop, Node.js 20+, Python 3.11+

## Quick Start (5 minutes)

```bash
# 1. Clone repository
git clone https://github.com/your-org/todo-app.git
cd todo-app

# 2. Set up environment
cp .env.example .env
# Edit .env with your API keys (see below)

# 3. Start services
docker-compose up

# 4. Access application
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
# API Health: http://localhost:8000/health
```

---

## Prerequisites Installation

### macOS
```bash
# Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install required tools
brew install git
brew install docker  # or Docker Desktop
brew install node
brew install python@3.11
brew install postgresql  # For local database (optional)

# Verify installations
git --version      # git version 2.40+
docker --version   # Docker version 24+
node --version     # v20+
python --version   # Python 3.11+
```

### Windows
```powershell
# Install Chocolatey (if not already installed)
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Install required tools
choco install git
choco install docker-desktop
choco install nodejs
choco install python311
choco install postgresql  # Optional

# Verify installations
git --version
docker --version
node --version
python --version
```

### Linux (Ubuntu/Debian)
```bash
# Update package manager
sudo apt-get update && sudo apt-get upgrade -y

# Install required tools
sudo apt-get install -y git curl build-essential
sudo snap install docker
sudo snap install node --classic
sudo apt-get install -y python3.11 python3.11-venv
sudo apt-get install -y postgresql

# Verify installations
git --version
docker --version
node --version
python3 --version
```

---

## Environment Configuration

### Create .env File

```bash
cp .env.example .env
```

Edit `.`.env` and add your API keys:

```env
# Database (use Neon PostgreSQL for managed service)
DATABASE_URL=postgresql://user:password@localhost:5432/todo_db

# Authentication Secret (generate with: openssl rand -base64 32)
BETTER_AUTH_SECRET=your-32-character-secret-here

# Cohere API (https://cohere.io)
COHERE_API_KEY=sk-your-cohere-key-here

# OpenAI API (https://openai.com)
OPENAI_API_KEY=sk-your-openai-key-here

# Frontend URL (for CORS)
FRONTEND_URL=http://localhost:3000

# Backend URL
BACKEND_URL=http://localhost:8000

# Environment
ENVIRONMENT=development
```

### Generate Secrets

```bash
# Generate BETTER_AUTH_SECRET
openssl rand -base64 32
# Output: abc123def456xyz789...

# Use the output in your .env file
```

---

## Database Setup

### Option 1: Neon PostgreSQL (Recommended)

```bash
# 1. Create account at https://neon.tech
# 2. Create new project (free tier available)
# 3. Copy connection string
# 4. Add to .env:
DATABASE_URL=postgresql://[user]:[password]@[host]/[database]?sslmode=require
```

### Option 2: Local PostgreSQL

```bash
# Start PostgreSQL (Docker)
docker run --name postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=todo_db \
  -p 5432:5432 \
  -d postgres:15

# Or use local installation
psql -U postgres -c "CREATE DATABASE todo_db;"

# Update .env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/todo_db
```

### Option 3: Docker Compose (Easiest)

```bash
# Already included in docker-compose.yml
# Just run: docker-compose up
# Database automatically created
```

---

## Running the Application

### Using Docker Compose (Recommended)

```bash
# Build and start all services
docker-compose up --build

# Expected output:
# todo-frontend | listening on 0.0.0.0:3000
# todo-backend  | Application startup complete
# todo-db       | database system is ready to accept connections
```

### Manual Setup (Frontend + Backend)

#### Terminal 1: Backend

```bash
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload

# Expected: Uvicorn running on http://0.0.0.0:8000
```

#### Terminal 2: Frontend

```bash
cd frontend

# Install dependencies
pnpm install  # or npm install

# Start development server
pnpm dev  # or npm run dev

# Expected: running at http://localhost:3000
```

---

## Verification

### Health Checks

```bash
# Check frontend
curl http://localhost:3000

# Check backend health
curl http://localhost:8000/health
# Expected: {"status":"healthy"}

# List available API endpoints
curl http://localhost:8000/docs
# Opens interactive API documentation
```

### Test Authentication

```bash
# Signup
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123!",
    "name": "Test User"
  }'

# Expected: Returns JWT token

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123!"
  }'

# Expected: Returns JWT token
```

### Test Chat API

```bash
TOKEN="your-jwt-token-here"

curl -X POST http://localhost:8000/api/chat/send \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "content": "add task buy groceries"
  }'

# Expected: Task created via AI
```

---

## Common Tasks

### Run Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
pnpm test
```

### Database Migrations

```bash
# Create new migration
cd backend
alembic revision --autogenerate -m "Add new table"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Format Code

```bash
# Python (backend)
cd backend
black app/
isort app/

# JavaScript (frontend)
cd frontend
pnpm format  # or npm run format
```

### Lint Code

```bash
# Python
cd backend
pylint app/
flake8 app/

# JavaScript
cd frontend
pnpm lint  # or npm run lint
```

---

## Troubleshooting

### Issue: Port Already in Use

```bash
# Find process using port
lsof -i :3000      # Frontend
lsof -i :8000      # Backend
lsof -i :5432      # Database

# Kill process
kill -9 <PID>

# Or use different port
docker-compose -f docker-compose.override.yml up
# (Edit docker-compose.override.yml to change ports)
```

### Issue: Database Connection Failed

```bash
# Verify DATABASE_URL
echo $DATABASE_URL

# Test connection
psql $DATABASE_URL -c "SELECT 1"

# Check if Postgres is running
docker ps | grep postgres

# Or start Postgres
docker-compose up postgres -d
```

### Issue: Dependencies Not Found

```bash
# Python backend
cd backend
pip install -r requirements.txt

# Node frontend
cd frontend
pnpm install  # Clear cache: pnpm store prune

# Clear Docker cache
docker-compose build --no-cache
```

### Issue: Port 3000 Shows Different App

```bash
# Stop all Docker containers
docker-compose down

# Remove old containers
docker rm -f $(docker ps -aq)

# Start fresh
docker-compose up --build
```

---

## Development Workflow

### 1. Create Feature Branch

```bash
git checkout -b feature/my-feature
```

### 2. Make Changes

```bash
# Frontend
cd frontend
# Edit components, styles, etc.

# Backend
cd backend
# Edit models, endpoints, etc.

# Changes auto-reload with --reload flag
```

### 3. Test Locally

```bash
# Run tests
pnpm test          # Frontend
pytest             # Backend

# Manual testing
curl http://localhost:3000      # Frontend
curl http://localhost:8000/docs # API docs
```

### 4. Commit Changes

```bash
git add .
git commit -m "feat: add my feature"
git push origin feature/my-feature
```

### 5. Create Pull Request

```bash
# Open GitHub and create PR
# CI/CD pipeline runs automatically
# Reviews and merge
```

---

## Useful Commands

```bash
# Docker
docker-compose up          # Start all services
docker-compose down        # Stop all services
docker-compose logs -f     # View logs
docker-compose ps          # List services
docker-compose exec backend bash  # Shell into container

# Frontend
pnpm dev          # Start development server
pnpm build        # Build for production
pnpm test         # Run tests
pnpm lint         # Check code quality

# Backend
uvicorn app.main:app --reload  # Start with auto-reload
pytest            # Run tests
pytest -v         # Verbose output
pytest -k test_name  # Run specific test
alembic upgrade head  # Apply migrations
alembic revision --autogenerate -m "message"  # Create migration

# Database
psql $DATABASE_URL      # Connect to database
\dt                     # List tables
\d table_name          # Describe table
```

---

## Next Steps

1. ✅ [Run Local Development](LOCAL_DEVELOPMENT.md) (you are here)
2. 🧪 [Run Tests](DOCKER_COMPOSE_TESTING.md)
3. 🚀 [Deploy to Minikube](MINIKUBE_DEPLOYMENT_TESTING.md)
4. 🔐 [Security Validation](SECURITY_VALIDATION.md)
5. 📋 [Production Deployment](PRODUCTION_DEPLOYMENT_RUNBOOK.md)

---

## Getting Help

- **API Documentation**: http://localhost:8000/docs (interactive Swagger)
- **Frontend Issues**: Check `frontend/.env` and browser console (F12)
- **Backend Issues**: Check `backend/logs/` and console output
- **Database Issues**: `psql $DATABASE_URL` to check connection
- **Docker Issues**: `docker-compose logs -f service-name`

---

**Happy developing!** 🚀

For issues or questions, open a GitHub issue with:
- Operating system
- Tool versions (docker --version, node --version, python --version)
- Error message and logs
- Steps to reproduce
