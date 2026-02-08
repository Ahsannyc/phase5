.PHONY: help setup dev test build deploy clean lint format

# Colors for output
BLUE=\033[0;34m
GREEN=\033[0;32m
YELLOW=\033[0;33m
NC=\033[0m # No Color

help: ## Show this help message
	@echo "${BLUE}Todo App - Make Targets${NC}"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "${GREEN}%-20s${NC} %s\n", $$1, $$2}'

# Setup & Installation
setup: ## Initial project setup (install deps, create .env)
	@echo "${YELLOW}Setting up project...${NC}"
	cp .env.example .env
	cd backend && pip install -r requirements.txt
	cd ../frontend && pnpm install
	@echo "${GREEN}✓ Setup complete${NC}"

env-check: ## Verify environment variables are set
	@echo "${YELLOW}Checking environment...${NC}"
	@test -f .env || (echo "${RED}Error: .env not found${NC}" && exit 1)
	@grep -q "DATABASE_URL" .env || (echo "${RED}Error: DATABASE_URL not set${NC}" && exit 1)
	@grep -q "BETTER_AUTH_SECRET" .env || (echo "${RED}Error: BETTER_AUTH_SECRET not set${NC}" && exit 1)
	@echo "${GREEN}✓ Environment OK${NC}"

# Development
dev: ## Start development servers (docker-compose)
	@echo "${YELLOW}Starting development environment...${NC}"
	docker-compose up --build

dev-local: ## Start dev servers locally (no Docker)
	@echo "${YELLOW}Starting frontend and backend locally...${NC}"
	@echo "${BLUE}Terminal 1: Starting backend...${NC}"
	@cd backend && uvicorn app.main:app --reload &
	@echo "${BLUE}Terminal 2: Starting frontend...${NC}"
	@cd frontend && pnpm dev &
	@echo "${GREEN}✓ Services starting on http://localhost:3000 and http://localhost:8000${NC}"

dev-stop: ## Stop development servers
	@echo "${YELLOW}Stopping development servers...${NC}"
	docker-compose down
	pkill -f "uvicorn"
	pkill -f "next dev"
	@echo "${GREEN}✓ Services stopped${NC}"

# Testing
test: test-backend test-frontend ## Run all tests

test-backend: ## Run backend tests
	@echo "${YELLOW}Running backend tests...${NC}"
	cd backend && pytest -v --cov=app

test-frontend: ## Run frontend tests
	@echo "${YELLOW}Running frontend tests...${NC}"
	cd frontend && pnpm test

test-integration: ## Run integration tests
	@echo "${YELLOW}Running integration tests...${NC}"
	./scripts/test-integration.sh

test-e2e: ## Run end-to-end tests (requires running server)
	@echo "${YELLOW}Running E2E tests...${NC}"
	cd frontend && pnpm test:e2e

test-load: ## Run load tests
	@echo "${YELLOW}Running load tests...${NC}"
	./scripts/load-test.sh

# Code Quality
lint: lint-backend lint-frontend ## Run all linters

lint-backend: ## Lint backend code
	@echo "${YELLOW}Linting backend...${NC}"
	cd backend && flake8 app/ && pylint app/

lint-frontend: ## Lint frontend code
	@echo "${YELLOW}Linting frontend...${NC}"
	cd frontend && pnpm lint

format: format-backend format-frontend ## Format all code

format-backend: ## Format backend code
	@echo "${YELLOW}Formatting backend...${NC}"
	cd backend && black app/ && isort app/

format-frontend: ## Format frontend code
	@echo "${YELLOW}Formatting frontend...${NC}"
	cd frontend && pnpm format

type-check: ## Run type checks
	@echo "${YELLOW}Type checking...${NC}"
	cd backend && mypy app/
	cd ../frontend && pnpm type-check

security-check: ## Run security checks
	@echo "${YELLOW}Running security checks...${NC}"
	cd backend && bandit -r app/
	cd ../frontend && npm audit
	gitleaks detect --source local

# Building
build: build-backend build-frontend ## Build all artifacts

build-backend: ## Build backend Docker image
	@echo "${YELLOW}Building backend image...${NC}"
	docker build -f docker/backend.Dockerfile -t todo-backend:latest .

build-frontend: ## Build frontend Docker image
	@echo "${YELLOW}Building frontend image...${NC}"
	docker build -f docker/frontend.Dockerfile -t todo-frontend:latest .

build-prod: ## Build production artifacts
	@echo "${YELLOW}Building for production...${NC}"
	cd frontend && pnpm build
	cd ../backend && pip freeze > requirements-prod.txt

# Docker Operations
docker-build: ## Build all Docker images
	@echo "${YELLOW}Building Docker images...${NC}"
	docker-compose build

docker-push: ## Push images to registry
	@echo "${YELLOW}Pushing images to registry...${NC}"
	docker tag todo-frontend:latest gcr.io/$(GCP_PROJECT)/todo-frontend:latest
	docker tag todo-backend:latest gcr.io/$(GCP_PROJECT)/todo-backend:latest
	docker push gcr.io/$(GCP_PROJECT)/todo-frontend:latest
	docker push gcr.io/$(GCP_PROJECT)/todo-backend:latest

docker-scan: ## Scan Docker images for vulnerabilities
	@echo "${YELLOW}Scanning Docker images...${NC}"
	trivy image todo-frontend:latest
	trivy image todo-backend:latest

# Kubernetes / Helm
k8s-setup: ## Setup Minikube cluster
	@echo "${YELLOW}Setting up Minikube...${NC}"
	minikube start --cpus=4 --memory=8192
	minikube addons enable ingress
	minikube addons enable metrics-server
	@echo "${GREEN}✓ Minikube ready${NC}"

k8s-deploy: ## Deploy to Kubernetes with Helm
	@echo "${YELLOW}Deploying to Kubernetes...${NC}"
	kubectl create namespace production || true
	kubectl create secret generic todo-secrets \
		--from-literal=DATABASE_URL="$(DATABASE_URL)" \
		--from-literal=BETTER_AUTH_SECRET="$(BETTER_AUTH_SECRET)" \
		-n production || true
	helm install todo-app ./k8s/helm/todo-app -n production || helm upgrade todo-app ./k8s/helm/todo-app -n production
	kubectl rollout status deployment/todo-app-backend -n production
	@echo "${GREEN}✓ Deployment complete${NC}"

k8s-logs: ## View logs from Kubernetes
	@echo "${YELLOW}Fetching logs...${NC}"
	kubectl logs -f deployment/todo-app-backend -n production

k8s-port-forward: ## Port forward from Kubernetes
	@echo "${YELLOW}Port forwarding...${NC}"
	kubectl port-forward svc/todo-app-backend 8000:8000 -n production

k8s-test: ## Test Kubernetes deployment
	@echo "${YELLOW}Testing Kubernetes deployment...${NC}"
	./scripts/k8s-test.sh

k8s-destroy: ## Destroy Kubernetes deployment
	@echo "${YELLOW}Destroying Kubernetes deployment...${NC}"
	helm uninstall todo-app -n production
	kubectl delete namespace production

# Database
db-migrate: ## Run database migrations
	@echo "${YELLOW}Running migrations...${NC}"
	cd backend && alembic upgrade head

db-migrate-create: ## Create new migration
	@echo "${YELLOW}Creating new migration...${NC}"
	cd backend && alembic revision --autogenerate -m "$(MSG)"

db-rollback: ## Rollback last migration
	@echo "${YELLOW}Rolling back...${NC}"
	cd backend && alembic downgrade -1

db-reset: ## Reset database (WARNING: deletes all data)
	@echo "${YELLOW}Resetting database...${NC}"
	cd backend && alembic downgrade base && alembic upgrade head

db-seed: ## Seed database with test data
	@echo "${YELLOW}Seeding database...${NC}"
	cd backend && python -m app.scripts.seed

# Documentation
docs: ## Generate documentation
	@echo "${YELLOW}Generating documentation...${NC}"
	cd backend && python -m pdoc -o docs/ app/
	@echo "${GREEN}✓ Documentation generated${NC}"

docs-serve: ## Serve documentation
	@echo "${YELLOW}Serving documentation...${NC}"
	cd docs && python -m http.server

# CI/CD
ci-local: lint test build ## Run full CI pipeline locally
	@echo "${GREEN}✓ CI pipeline complete${NC}"

ci-deploy: ci-local docker-push k8s-deploy ## Full CI/CD pipeline
	@echo "${GREEN}✓ CI/CD pipeline complete${NC}"

# Cleanup
clean: ## Clean build artifacts and cache
	@echo "${YELLOW}Cleaning...${NC}"
	rm -rf frontend/.next frontend/dist backend/__pycache__ backend/.pytest_cache
	find . -type d -name "__pycache__" -exec rm -rf {} + || true
	find . -type f -name "*.pyc" -delete
	docker-compose down -v
	@echo "${GREEN}✓ Cleanup complete${NC}"

clean-docker: ## Remove all Docker containers and images
	@echo "${YELLOW}Removing Docker artifacts...${NC}"
	docker-compose down -v
	docker rmi todo-frontend todo-backend || true
	@echo "${GREEN}✓ Docker cleanup complete${NC}"

# Utilities
shell-backend: ## Open shell in backend container
	docker-compose exec backend bash

shell-frontend: ## Open shell in frontend container
	docker-compose exec frontend bash

shell-db: ## Open PostgreSQL shell
	docker-compose exec postgres psql -U postgres todo_db

version: ## Show version info
	@echo "${BLUE}Version Info${NC}"
	@echo "Node: $$(node --version)"
	@echo "Python: $$(python --version)"
	@echo "Docker: $$(docker --version)"
	@echo "Docker Compose: $$(docker-compose --version)"

# Default target
.DEFAULT_GOAL := help
