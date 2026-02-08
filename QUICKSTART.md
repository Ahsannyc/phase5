# Phase 4 Deployment Quickstart Guide

**Get the Todo app running locally in 5 minutes, or on Kubernetes in 15 minutes.**

---

## 🚀 Option 1: Local Development (Docker Compose)

### Prerequisites
- Docker Desktop (with Docker Compose v2)
- Git
- 30MB disk space minimum

### Setup (5 minutes)

```bash
# 1. Clone and enter project
git clone <repo-url>
cd todo-app

# 2. Configure environment
cp .env.example .env

# Edit .env with your API keys:
#   DATABASE_URL (get from Neon.tech)
#   BETTER_AUTH_SECRET (any 32+ character string)
#   COHERE_API_KEY (from cohere.io)
#   OPENAI_API_KEY (from openai.com)
nano .env  # or use your editor
```

### Run (1 minute)

```bash
# Start all services
docker-compose up

# Wait for output like:
# todo-frontend | ...
# todo-backend  | Uvicorn running on http://0.0.0.0:8000

# In another terminal, test:
curl http://localhost:3000              # Frontend
curl http://localhost:8000/health       # Backend health
```

### Access

- **Frontend**: http://localhost:3000 (login page)
- **Backend API**: http://localhost:8000 (health check)
- **Chatbot**: Create tasks by talking to the AI after login

### Stop

```bash
docker-compose down        # Stop containers
docker-compose down -v     # Stop and remove data
```

### Troubleshooting Local

| Issue | Solution |
|-------|----------|
| Port already in use | Edit docker-compose.yml ports, or `lsof -i :3000; kill -9 <PID>` |
| Build fails | `docker-compose build --no-cache` |
| Secrets error | Check `.env` has valid API keys |
| Can't connect to DB | Verify DATABASE_URL is correct and Neon server is online |

**See**: [DOCKER_COMPOSE_TESTING.md](DOCKER_COMPOSE_TESTING.md) for detailed testing procedures

---

## ☸️ Option 2: Kubernetes (Minikube)

### Prerequisites
- Docker Desktop (for Minikube driver)
- Minikube (`brew install minikube` or download)
- Helm 3.14+ (`brew install helm`)
- kubectl (included with Minikube)
- 8GB RAM + 4 CPU (configure Minikube)
- ~10 minutes

### Setup (5 minutes)

#### 1. Start Minikube

```bash
# Start cluster with adequate resources
minikube start --driver=docker --cpus=4 --memory=8192

# Verify cluster is running
minikube status
# Output should show:
# minikube: Running
# kubelet: Running
# ...

# Get cluster IP for /etc/hosts
MINIKUBE_IP=$(minikube ip)
echo "Your Minikube IP: $MINIKUBE_IP"
```

#### 2. Enable Addons

```bash
# Enable ingress controller
minikube addons enable ingress

# Enable metrics for resource monitoring
minikube addons enable metrics-server

# Verify
kubectl get pods -n ingress-nginx
# Should show ingress-nginx-controller Running
```

#### 3. Configure Environment

```bash
# Setup environment
cp .env.example .env

# Edit .env with API keys (same as local setup)
# DATABASE_URL, BETTER_AUTH_SECRET, COHERE_API_KEY, OPENAI_API_KEY
nano .env
```

#### 4. Build Images in Minikube

```bash
# Use Minikube's Docker environment
eval $(minikube docker-env)

# Build images (they'll be stored in Minikube)
docker-compose build

# Verify images are in Minikube
docker images | grep todo
```

### Deploy (5 minutes)

#### 1. Create Kubernetes Secret

```bash
# Create secret from .env values
kubectl create secret generic todo-secrets \
  --from-literal=DATABASE_URL="$(grep DATABASE_URL .env | cut -d= -f2)" \
  --from-literal=BETTER_AUTH_SECRET="$(grep BETTER_AUTH_SECRET .env | cut -d= -f2)" \
  --from-literal=COHERE_API_KEY="$(grep COHERE_API_KEY .env | cut -d= -f2)" \
  --from-literal=OPENAI_API_KEY="$(grep OPENAI_API_KEY .env | cut -d= -f2)"

# Verify
kubectl get secret todo-secrets
```

#### 2. Deploy with Helm

```bash
# Install Helm chart
helm install todo-app ./k8s/helm/todo-app

# Verify deployment
helm status todo-app

# Watch pods starting
kubectl get pods -w

# Wait for all pods to be Running and Ready
kubectl get pods
# Output example:
# NAME                              READY   STATUS    RESTARTS   AGE
# todo-app-frontend-xxx             1/1     Running   0          30s
# todo-app-backend-xxx              1/1     Running   0          30s
```

#### 3. Configure Ingress Access

```bash
# Add Minikube IP to /etc/hosts
MINIKUBE_IP=$(minikube ip)
echo "$MINIKUBE_IP todo.local" | sudo tee -a /etc/hosts

# Or on macOS/Windows:
sudo nano /etc/hosts
# Add line: <minikube-ip> todo.local

# Verify
curl http://todo.local
# Should return HTML from frontend
```

### Access (5 minutes)

- **Frontend**: http://todo.local (in browser)
- **Backend**: http://todo.local/api (API routes)
- **Health check**: `curl http://todo.local/api/health`

### Dashboard & Monitoring

```bash
# Open Kubernetes dashboard
minikube dashboard

# View pod logs
kubectl logs deployment/todo-app-backend
kubectl logs deployment/todo-app-frontend

# Watch events
kubectl get events -w

# Resource usage
kubectl top pods
kubectl top nodes
```

### Common Kubernetes Commands

```bash
# Check pod status
kubectl get pods

# Describe pod (for debugging)
kubectl describe pod <pod-name>

# View logs
kubectl logs pod/<pod-name>
kubectl logs -f deployment/todo-app-backend  # Follow logs

# Port forward (if ingress not working)
kubectl port-forward svc/todo-app-frontend 3000:3000
kubectl port-forward svc/todo-app-backend 8000:8000

# Scale replicas
kubectl scale deployment/todo-app-backend --replicas=3

# Or via Helm
helm upgrade todo-app ./k8s/helm/todo-app --set backend.replicas=3

# Check scaling
kubectl get pods | grep backend
```

### Helm Chart Management

```bash
# View chart values
helm show values ./k8s/helm/todo-app

# Template generation (without deploying)
helm template todo-app ./k8s/helm/todo-app

# Lint chart for errors
helm lint ./k8s/helm/todo-app

# Upgrade deployment
helm upgrade todo-app ./k8s/helm/todo-app

# Rollback to previous version
helm rollback todo-app 0

# Uninstall
helm uninstall todo-app
```

### Troubleshooting Kubernetes

| Issue | Solution |
|-------|----------|
| Pods not starting | `kubectl describe pod <name>` - check events |
| CrashLoopBackOff | Check logs: `kubectl logs <pod>` |
| ImagePullBackOff | Images not built: `docker-compose build` in Minikube context |
| Ingress not working | Verify addon: `kubectl get pods -n ingress-nginx` |
| Connection timeout | Add to /etc/hosts: `<minikube-ip> todo.local` |
| Secret not found | Recreate: `kubectl delete secret todo-secrets` then create again |
| Pod stuck terminating | Force delete: `kubectl delete pod <name> --grace-period=0 --force` |

### AI-Powered Operations (Optional)

```bash
# Install kubectl-ai (if not already installed)
pip install kubectl-ai

# Natural language commands
kubectl-ai "scale deployment todo-backend to 3 replicas"
kubectl-ai "show me the health status of all pods"
kubectl-ai "explain why the backend pod keeps restarting"

# Cluster analysis with kagent
kagent "cluster health analysis"
```

### Cleanup

```bash
# Remove deployment
helm uninstall todo-app

# Stop Minikube
minikube stop

# Delete Minikube cluster (full cleanup)
minikube delete
```

---

## 🔄 Comparing Local vs Kubernetes

| Feature | Docker Compose | Minikube |
|---------|---|---|
| Setup time | 2 min | 10 min |
| Startup time | <1 min | ~2 min |
| Scaling | Manual docker-compose | `kubectl scale` or `helm upgrade` |
| Zero-downtime | Not tested | ✅ Verified |
| Health checks | ✅ Built-in | ✅ Probes configured |
| Storage | Local volumes | None (external DB) |
| Multi-machine | ❌ | ✅ Ready for cloud |
| Cost | Free | Free (local) |
| Best for | Development | Testing production setup |

---

## 📊 Testing Your Deployment

### Local (Docker Compose)

```bash
# In one terminal: Start services
docker-compose up

# In another terminal: Run tests
# 1. Test frontend
curl http://localhost:3000

# 2. Test backend
curl http://localhost:8000/health

# 3. Test chatbot
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"create task","user_id":1}'

# 4. Test data persistence
docker-compose restart backend
sleep 3
curl http://localhost:8000/health
```

### Kubernetes (Minikube)

```bash
# 1. Check pods running
kubectl get pods

# 2. Get logs
kubectl logs -f deployment/todo-app-backend

# 3. Port forward for testing
kubectl port-forward svc/todo-app-frontend 3000:3000

# 4. Test via ingress
curl http://todo.local

# 5. Test scaling
kubectl scale deployment/todo-app-backend --replicas=3
kubectl get pods -w  # Watch scaling

# 6. Kill a pod (test recovery)
kubectl delete pod <backend-pod-name>
kubectl get pods -w  # Watch replacement created

# 7. View resource usage
kubectl top pods
```

---

## 🎥 Demo: 90-Second Walkthrough

For a live demo showing all features:

```bash
# 1. Start docker-compose (30s)
time docker-compose up

# 2. Test frontend (10s)
curl http://localhost:3000 -I

# 3. Test chatbot (20s)
curl -X POST http://localhost:8000/api/chat ...

# 4. Test Minikube (30s)
minikube start
helm install todo-app ./k8s/helm/todo-app
curl http://todo.local

# Total: ~90 seconds for full demo
```

---

## 📚 Next Steps

1. **Local Testing**: Follow Option 1 above, then see [DOCKER_COMPOSE_TESTING.md](DOCKER_COMPOSE_TESTING.md)
2. **Kubernetes Testing**: Follow Option 2 above, then test all scenarios
3. **Production**: Swap Minikube for real Kubernetes (EKS, GKE, AKS)

---

## 🆘 Need Help?

- **Docker Compose issues**: See [DOCKER_COMPOSE_TESTING.md](DOCKER_COMPOSE_TESTING.md)
- **Kubernetes issues**: Check [README.md](README.md) troubleshooting section
- **Full guide**: See [k8s/deployment.md](k8s/deployment.md)
- **Architecture**: See [specs/001-cloud-native-deploy/](specs/001-cloud-native-deploy/)

---

**You're all set!** 🎉

Choose your path:
- 🏃 **5 min**: `docker-compose up` (Option 1)
- ⚙️ **15 min**: `helm install todo-app ./k8s/helm/todo-app` (Option 2)
