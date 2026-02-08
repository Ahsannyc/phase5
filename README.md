# Todo Application - Complete Stack

A cloud-native, AI-powered task management application with multi-phase development:

- **Phase 1-2**: Core full-stack (Next.js frontend, FastAPI backend, JWT auth)
- **Phase 3**: AI chatbot integration (MCP tools, OpenAI Agents SDK, Cohere LLM)
- **Phase 4**: Cloud-native deployment (Docker, Kubernetes, Helm, AIOps)

---

## Phase 4: Cloud-Native Deployment

Deploy the complete Todo app locally or to Kubernetes with zero-downtime scaling, AI-powered operations, and production-ready security.

### Quick Start: Docker Compose (Local Development)

```bash
# 1. Copy environment template and fill in API keys
cp .env.example .env
# Edit .env: DATABASE_URL, COHERE_API_KEY, OPENAI_API_KEY, BETTER_AUTH_SECRET

# 2. Start all services
docker-compose up

# 3. Access the app
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# Backend health check: http://localhost:8000/health

# 4. Cleanup
docker-compose down
```

**What you get**:
- ✅ Frontend (Next.js) on port 3000
- ✅ Backend (FastAPI) on port 8000
- ✅ Database connection (Neon PostgreSQL via DATABASE_URL)
- ✅ Chatbot fully functional with natural language task management

### Quick Start: Kubernetes + Helm (Production-Ready)

```bash
# 1. Start Minikube cluster
minikube start --driver=docker --cpus=4 --memory=8192

# 2. Enable addons
minikube addons enable ingress
minikube addons enable metrics-server

# 3. Set environment variables
cp .env.example .env
# Edit .env with your API keys

# 4. Create Kubernetes Secret
kubectl create secret generic todo-secrets \
  --from-literal=DATABASE_URL=$(grep DATABASE_URL .env | cut -d= -f2) \
  --from-literal=BETTER_AUTH_SECRET=$(grep BETTER_AUTH_SECRET .env | cut -d= -f2) \
  --from-literal=COHERE_API_KEY=$(grep COHERE_API_KEY .env | cut -d= -f2) \
  --from-literal=OPENAI_API_KEY=$(grep OPENAI_API_KEY .env | cut -d= -f2)

# 5. Deploy via Helm
helm install todo-app ./k8s/helm/todo-app

# 6. Add ingress to /etc/hosts
echo "$(minikube ip) todo.local" >> /etc/hosts

# 7. Access the app
# App URL: http://todo.local
# Watch pods: kubectl get pods -w
# View logs: kubectl logs -f deployment/todo-backend

# 8. Cleanup
helm uninstall todo-app
minikube stop
```

**What you get**:
- ✅ Multi-pod deployment (frontend, backend replicas)
- ✅ Automatic health checks (liveness, readiness probes)
- ✅ Graceful shutdown and zero-downtime scaling
- ✅ Pod recovery (automatic restart on failure)
- ✅ Secret management (API keys via Kubernetes Secrets)
- ✅ Ingress routing (external access via todo.local)

### Phase 4 Features

#### 1. Docker Containerization

Multi-stage Dockerfiles for minimal, secure images:

```bash
# Frontend: node:20-alpine → nginx:alpine (<150MB)
# - Build Next.js app with pnpm
# - Serve via nginx from .next/standalone
# - Non-root user (nginx)
# - Health check on port 80

# Backend: python:3.11-slim → python:3.11-slim (<300MB)
# - Build with poetry/uv, virtualenv copied
# - Run via uvicorn (4 workers)
# - Non-root user (appuser:1000)
# - Health check on /health endpoint
```

#### 2. Kubernetes Deployment (Helm Chart)

Production-ready Helm chart with full customization:

```bash
# View chart structure
tree k8s/helm/todo-app/

# Template generation
helm template todo-app ./k8s/helm/todo-app > manifests.yaml

# Helm operations
helm install todo-app ./k8s/helm/todo-app              # Deploy
helm upgrade todo-app ./k8s/helm/todo-app              # Update
helm uninstall todo-app                                 # Remove
helm upgrade todo-app ./k8s/helm/todo-app --set backend.replicas=3  # Scale
```

#### 3. AI-Powered Kubernetes Operations (kubectl-ai / kagent)

Natural language cluster management:

```bash
# Scale deployment
kubectl-ai "scale deployment todo-backend to 3 replicas"

# Cluster diagnostics
kagent "cluster health analysis"

# Pod troubleshooting
kubectl-ai "explain why pod todo-backend-xyz restarted"

# Resource optimization
kagent "resource optimization recommendations"
```

### Documentation

- **[deployment.md](k8s/deployment.md)** - Complete deployment guide with step-by-step instructions, examples, and troubleshooting
- **[specs/001-cloud-native-deploy/](specs/001-cloud-native-deploy/)** - Full specification, architecture plan, and implementation tasks
  - `spec.md` - Feature requirements and acceptance criteria
  - `plan.md` - Technical architecture and design decisions
  - `research.md` - Research and decision documentation
  - `contracts/` - Docker image and Kubernetes resource contracts
  - `tasks.md` - 109 implementation tasks (109 tasks for full coverage, 76 for MVP)

### Project Structure (Phase 4 Additions)

```
.
├── docker/                    # Dockerfiles (Phase 4)
│   ├── frontend.Dockerfile
│   └── backend.Dockerfile
├── k8s/                       # Kubernetes resources (Phase 4)
│   ├── helm/
│   │   └── todo-app/
│   │       ├── Chart.yaml
│   │       ├── values.yaml
│   │       ├── templates/
│   │       │   ├── deployment-frontend.yaml
│   │       │   ├── deployment-backend.yaml
│   │       │   ├── service-frontend.yaml
│   │       │   ├── service-backend.yaml
│   │       │   ├── ingress.yaml
│   │       │   ├── secret.yaml
│   │       │   └── _helpers.tpl
│   └── deployment.md          # Deployment guide
├── docker-compose.yml         # Local orchestration (Phase 4)
├── .dockerignore              # Docker build ignore (Phase 4)
├── .env.example               # Environment template
├── frontend/                  # Next.js app (Phases 1-3)
├── backend/                   # FastAPI app (Phases 1-3)
├── specs/                     # Specifications (all phases)
└── README.md                  # This file
```

### System Requirements

- **Docker Desktop** (with Docker Compose v2)
- **Minikube** (for Kubernetes testing)
- **Helm 3.14+** (for chart deployment)
- **kubectl** (for cluster management)
- **kubectl-ai** (for AI-assisted operations - optional but recommended)
- **kagent** (for cluster analytics - optional but recommended)

### Environment Variables

All sensitive values go in `.env` (never committed):

```bash
DATABASE_URL=postgresql://user:pass@host/db?sslmode=require
BETTER_AUTH_SECRET=secret-key-min-32-chars
COHERE_API_KEY=your-cohere-api-key
OPENAI_API_KEY=your-openai-api-key
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=your-chatkit-domain
```

For Kubernetes, these are injected via `Kubernetes Secrets` at deployment time (see deployment.md).

### Key Commands

```bash
# Local Development
docker-compose up                    # Start all services
docker-compose down                  # Stop all services
docker-compose logs -f               # View logs
docker-compose ps                    # Service status

# Kubernetes
minikube start                       # Start cluster
minikube status                      # Cluster status
minikube ip                          # Get IP for /etc/hosts
kubectl get pods                     # List pods
kubectl logs pod/NAME                # View pod logs
kubectl describe pod/NAME            # Pod details
kubectl get svc                      # List services
kubectl get ingress                  # List ingress rules

# Helm
helm install todo-app ./k8s/helm/todo-app    # Deploy
helm list                            # List releases
helm status todo-app                 # Release status
helm upgrade todo-app ./k8s/helm/todo-app    # Update
helm uninstall todo-app              # Remove
helm lint ./k8s/helm/todo-app        # Validate chart

# AI Operations (Phase 4 Innovation)
kubectl-ai "scale deployment to 3 replicas"  # Natural language scaling
kagent "cluster health"              # AI health analysis
```

### Success Criteria (Phase 4)

- ✅ docker-compose up starts all services in <60 seconds
- ✅ Helm deployment reaches Running state in <90 seconds
- ✅ Zero downtime during horizontal scaling (replicas 1→3)
- ✅ Pod recovery in <5 seconds after deletion
- ✅ Chatbot works inside Kubernetes
- ✅ kubectl-ai and kagent perform operations without errors
- ✅ Zero secrets exposed (images, Git, logs)
- ✅ <90 second demo video shows complete flow

### Next Steps

1. **Review Specifications**: Read [specs/001-cloud-native-deploy/spec.md](specs/001-cloud-native-deploy/spec.md)
2. **Setup Environment**: Copy `.env.example` to `.env` and fill in API keys
3. **Deploy Locally**: Run `docker-compose up` and test chatbot
4. **Deploy to K8s**: Follow [k8s/deployment.md](k8s/deployment.md) for Minikube deployment
5. **Run AI Ops**: Execute kubectl-ai and kagent commands from deployment.md

---

**Phase 4 Status**: 🚀 **Implementation in progress**

For detailed deployment instructions and troubleshooting, see [k8s/deployment.md](k8s/deployment.md).

For full specifications, architecture, and implementation tasks, see [specs/001-cloud-native-deploy/](specs/001-cloud-native-deploy/).
