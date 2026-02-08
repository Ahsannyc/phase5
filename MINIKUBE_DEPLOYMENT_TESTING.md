# Phase 4: Minikube & Kubernetes Deployment Testing Guide

**Phase**: 4 (Cloud-Native Deployment - Kubernetes Testing)
**Tasks**: T042-T059 (Minikube setup, Helm deployment, K8s validation, ingress testing)
**Duration**: ~2-3 hours (hands-on Kubernetes testing and validation)

## Overview

This guide documents comprehensive testing for Kubernetes deployment using Minikube and Helm charts. The infrastructure components are complete:
- ✅ Helm chart with all manifests (deployments, services, ingress, secrets)
- ✅ Minikube configuration for local development
- ✅ Docker images (frontend, backend) ready in Minikube
- ✅ Environment configuration (.env) ready for secret injection

**Next**: Execute Minikube deployment and validation tests locally.

---

## Prerequisites

- **Minikube**: v1.30+ installed (`minikube version`)
- **kubectl**: v1.24+ installed (usually bundled with Minikube)
- **Helm**: v3.14+ installed (`helm version`)
- **Docker Desktop** or Docker daemon (for building images in Minikube context)
- **System Resources**: 8GB RAM, 4 CPU cores minimum allocated to Minikube
- **Network**: Ability to modify /etc/hosts (or access via localhost)
- **.env file**: With DATABASE_URL, BETTER_AUTH_SECRET, COHERE_API_KEY, OPENAI_API_KEY

## Quick Setup

```bash
# 1. Start Minikube with sufficient resources
minikube start --driver=docker --cpus=4 --memory=8192 --addons=ingress

# 2. Verify Minikube is running
minikube status
# Output should show: Running (cluster), Running (kubelet), etc.

# 3. Get Minikube IP (needed for /etc/hosts)
MINIKUBE_IP=$(minikube ip)
echo "Minikube IP: $MINIKUBE_IP"

# 4. Enable required addons
minikube addons enable ingress
minikube addons enable metrics-server

# 5. Verify addons are enabled
kubectl get pods -n ingress-nginx
# Should show ingress-nginx-controller pod Running

# 6. Build images in Minikube context
eval $(minikube docker-env)
docker-compose build

# 7. Verify images are in Minikube
docker images | grep todo

# 8. Create Kubernetes secret from .env
kubectl create secret generic todo-secrets \
  --from-literal=DATABASE_URL="$(grep DATABASE_URL .env | cut -d= -f2)" \
  --from-literal=BETTER_AUTH_SECRET="$(grep BETTER_AUTH_SECRET .env | cut -d= -f2)" \
  --from-literal=COHERE_API_KEY="$(grep COHERE_API_KEY .env | cut -d= -f2)" \
  --from-literal=OPENAI_API_KEY="$(grep OPENAI_API_KEY .env | cut -d= -f2)"

# 9. Deploy with Helm
helm install todo-app ./k8s/helm/todo-app

# 10. Add Minikube IP to /etc/hosts
echo "$MINIKUBE_IP todo.local" | sudo tee -a /etc/hosts
```

---

## Phase 4 Kubernetes Testing Tasks (T042-T059)

### Section 1: Minikube Cluster Setup (T042-T045)

#### T042: Minikube Initialization

```bash
# Start Minikube with Docker driver and sufficient resources
minikube start \
  --driver=docker \
  --cpus=4 \
  --memory=8192 \
  --disk-size=40g

# Expected output:
# 😄  minikube v1.31.0 on Linux (amd64)
# ✨  Using the docker driver based on existing profile
# 👍  Starting cluster control-plane node minikube in cluster minikube
# 🚀  Launching Kubernetes v1.27.0 on Docker
# ...
# 🎉  minikube successfully started

# Verify cluster status
minikube status

# Expected output:
# minikube
# type: Control Plane
# host: Running
# kubelet: Running
# apiserver: Running
# kubeconfig: Configured
```

**Pass Criteria**:
- ✅ Minikube starts without errors
- ✅ Cluster shows Running status for all components
- ✅ kubectl can access cluster: `kubectl get nodes`
- ✅ `kubectl version` shows both client and server versions

#### T043: Enable Required Addons

```bash
# Enable Ingress addon (required for ingress.yaml)
minikube addons enable ingress

# Expected output:
# ❌ Enabling addon ingress...
# ✅ ingress was successfully enabled

# Enable metrics server (for resource monitoring)
minikube addons enable metrics-server

# Expected output:
# ✅ metrics-server was successfully enabled

# Verify addons are enabled
minikube addons list | grep -E "ingress|metrics"

# Expected output:
# | ingress                    | minikube | enabled ✓   | ...
# | metrics-server             | minikube | enabled ✓   | ...

# Verify ingress controller is running
kubectl get pods -n ingress-nginx

# Expected output:
# NAME                                        READY   STATUS    RESTARTS   AGE
# ingress-nginx-admission-create-xxxxx        0/1     Completed   0        10s
# ingress-nginx-admission-patch-xxxxx         0/1     Completed   0        10s
# ingress-nginx-controller-xxxxxxxx           1/1     Running     0        10s

# Verify metrics-server
kubectl get deployment metrics-server -n kube-system

# Expected: 1 replica Running
```

**Pass Criteria**:
- ✅ Ingress addon enabled and controller running
- ✅ Metrics-server addon enabled and operational
- ✅ No pending pods or CrashLoopBackOff states
- ✅ `kubectl top nodes` shows resource usage

#### T044: Get Minikube IP & Configure Networking

```bash
# Get Minikube IP (varies per machine)
MINIKUBE_IP=$(minikube ip)
echo "Minikube IP: $MINIKUBE_IP"

# Expected output:
# Minikube IP: 192.168.49.2

# Add to /etc/hosts for DNS resolution
echo "$MINIKUBE_IP todo.local" | sudo tee -a /etc/hosts

# Verify entry was added
grep todo.local /etc/hosts

# Expected output:
# 192.168.49.2 todo.local

# Test DNS resolution
ping -c 1 todo.local

# Expected: Should resolve to Minikube IP
```

**Pass Criteria**:
- ✅ Minikube IP retrieved successfully
- ✅ Entry added to /etc/hosts
- ✅ `ping todo.local` resolves to Minikube IP
- ✅ Same IP can be used for both frontend and backend (via ingress routing)

#### T045: Verify kubectl Configuration

```bash
# Check kubectl can access Minikube
kubectl cluster-info

# Expected output:
# Kubernetes control plane is running at https://...
# CoreDNS is running at https://...

# Verify context
kubectl config current-context

# Expected output:
# minikube

# List available contexts
kubectl config get-contexts

# Expected to show minikube as current context (*minikube)

# Check API server connectivity
kubectl get nodes

# Expected:
# NAME       STATUS   ROLES           AGE     VERSION
# minikube   Ready    control-plane   XXXm    vX.X.X
```

**Pass Criteria**:
- ✅ kubectl connected to Minikube cluster
- ✅ Current context is "minikube"
- ✅ At least one node (minikube) in Ready status
- ✅ Kubernetes version matches expected (1.20+)

---

### Section 2: Docker Image Building (T046-T048)

#### T046: Setup Minikube Docker Environment

```bash
# Use Minikube's Docker daemon for image building
eval $(minikube docker-env)

# Verify Docker is using Minikube
docker ps

# Expected: Should show Minikube internal containers

# Check Docker info
docker info | grep -i server

# Expected output:
# Server Version: X.X.X (Minikube's Docker version)

# Verify you're using Minikube's Docker
echo $DOCKER_HOST

# Expected output:
# unix:///home/user/.minikube/machines/minikube/docker.sock
```

**Pass Criteria**:
- ✅ eval command sets Docker env variables correctly
- ✅ docker ps shows Minikube internal containers
- ✅ DOCKER_HOST points to Minikube socket
- ✅ Subsequent docker commands use Minikube daemon

#### T047: Build Frontend Image in Minikube

```bash
# Build frontend image using Minikube's Docker
docker build -f docker/frontend.Dockerfile -t todo-frontend:latest .

# Expected output:
# [+] Building 45.2s (12/12) FINISHED
# ...
# => exporting to image
# => => writing image sha256:...
# => => naming to docker.io/library/todo-frontend:latest

# Verify image is in Minikube
docker images | grep todo-frontend

# Expected output:
# todo-frontend           latest    sha256:...      XX seconds ago   XXmb

# Check image size
docker images todo-frontend --format "{{.Size}}"

# Expected: Should be < 150MB (from architectural requirements)

# Inspect image layers
docker history todo-frontend:latest

# Expected:
# - No COHERE_API_KEY in environment
# - No OPENAI_API_KEY in environment
# - No DATABASE_URL in environment
# - Final image uses node:20-alpine as base
```

**Pass Criteria**:
- ✅ Image builds successfully without errors
- ✅ Image size < 150MB (for Next.js standalone)
- ✅ Image runs as non-root user (nginx, UID 101)
- ✅ No secrets embedded in image layers

#### T048: Build Backend Image in Minikube

```bash
# Build backend image using Minikube's Docker
docker build -f docker/backend.Dockerfile -t todo-backend:latest .

# Expected output (multi-stage build):
# [+] Building 120.5s (15/15) FINISHED
# => [builder 1/2] FROM python:3.11-slim
# ...
# => [stage-1 2/2] COPY --from=builder /opt/venv ...

# Verify image is in Minikube
docker images | grep todo-backend

# Expected output:
# todo-backend            latest    sha256:...      XX seconds ago   XXmb

# Check image size
docker images todo-backend --format "{{.Size}}"

# Expected: Should be < 300MB (from architectural requirements)

# Inspect for security issues
docker history todo-backend:latest | grep -iE "pip install|secret|password"

# Expected: Should NOT see pip install commands in final layer

# Test image runs
docker run --rm todo-backend:latest whoami

# Expected output:
# appuser (or UID 1000)

# Verify health check is defined
docker inspect todo-backend:latest | jq '.Config.Healthcheck'

# Expected: Should show healthcheck command
```

**Pass Criteria**:
- ✅ Image builds successfully without errors
- ✅ Image size < 300MB (for Python FastAPI)
- ✅ Image runs as non-root user (appuser, UID 1000)
- ✅ No secrets embedded in final image layer
- ✅ Health check command defined

---

### Section 3: Kubernetes Secret Management (T049-T050)

#### T049: Create Kubernetes Secret from Environment

```bash
# Create secret from .env file values
kubectl create secret generic todo-secrets \
  --from-literal=DATABASE_URL="$(grep DATABASE_URL .env | cut -d= -f2)" \
  --from-literal=BETTER_AUTH_SECRET="$(grep BETTER_AUTH_SECRET .env | cut -d= -f2)" \
  --from-literal=COHERE_API_KEY="$(grep COHERE_API_KEY .env | cut -d= -f2)" \
  --from-literal=OPENAI_API_KEY="$(grep OPENAI_API_KEY .env | cut -d= -f2)"

# Expected output:
# secret/todo-secrets created

# Verify secret exists
kubectl get secret todo-secrets

# Expected output:
# NAME           TYPE     DATA   AGE
# todo-secrets   Opaque   4      5s

# Inspect secret (DO NOT output values)
kubectl get secret todo-secrets -o jsonpath='{.data.DATABASE_URL}' | base64 -d

# Expected: Should show your DATABASE_URL (verify it's correct)

# Verify all keys are present
kubectl get secret todo-secrets -o jsonpath='{.data}'

# Expected: Should show 4 keys: DATABASE_URL, BETTER_AUTH_SECRET, COHERE_API_KEY, OPENAI_API_KEY
```

**Pass Criteria**:
- ✅ Secret created successfully
- ✅ Secret contains 4 keys (all API keys and DB URL)
- ✅ Secret values are base64 encoded
- ✅ Secret can be mounted in pod spec

#### T050: Verify Secret Injection into Pods (Post-Deployment)

```bash
# This test is performed AFTER pods are deployed (see T054)
# Run after: helm install todo-app ./k8s/helm/todo-app

# Check backend pod has secret mounted
BACKEND_POD=$(kubectl get pods -l app=todo-backend -o jsonpath='{.items[0].metadata.name}')

# Verify environment variables are injected
kubectl exec $BACKEND_POD -- env | grep -E "DATABASE_URL|COHERE_API_KEY"

# Expected output:
# DATABASE_URL=postgresql://...
# COHERE_API_KEY=sk-...

# Verify secret is mounted as volume (optional implementation)
kubectl exec $BACKEND_POD -- ls -la /var/run/secrets/kubernetes.io/serviceaccount/

# Expected: Should show mounted serviceaccount token and ca.crt

# Test that backend can connect to database
kubectl exec $BACKEND_POD -- curl -s http://localhost:8000/health | jq .

# Expected:
# {
#   "status": "healthy"
# }
```

**Pass Criteria**:
- ✅ Secret successfully injected into pod environment
- ✅ All 4 secret values available as env vars in pod
- ✅ Backend can use DATABASE_URL to connect (health check passes)
- ✅ No secrets exposed in pod description: `kubectl describe pod <pod>`

---

### Section 4: Helm Chart Deployment (T051-T054)

#### T051: Helm Chart Lint & Validation

```bash
# Lint the Helm chart for errors
helm lint ./k8s/helm/todo-app

# Expected output:
# ==> Linting ./k8s/helm/todo-app
# [INFO] Chart is consistent
# [INFO] Icon file is missing, but not required
# 1 chart(s) linted, 0 error(s)

# Generate templates without deploying (dry-run)
helm template todo-app ./k8s/helm/todo-app

# Expected: Should output all Kubernetes manifests in order:
# ---
# # Source: todo-app/templates/secret.yaml
# apiVersion: v1
# kind: Secret
# ...
# ---
# # Source: todo-app/templates/deployment-frontend.yaml
# apiVersion: apps/v1
# kind: Deployment
# ...

# Verify template rendering with custom values
helm template todo-app ./k8s/helm/todo-app \
  --set frontend.replicas=3 \
  --set backend.replicas=2 | grep replicas

# Expected: Should show replicas: 3 for frontend, replicas: 2 for backend

# Test Helm dry-run (validate without creating resources)
helm install todo-app ./k8s/helm/todo-app --dry-run --debug

# Expected: Should output all resources without actually creating them
```

**Pass Criteria**:
- ✅ Helm lint passes with 0 errors
- ✅ helm template generates valid YAML
- ✅ All required resources included (secret, deployments, services, ingress)
- ✅ Values can be overridden at install time
- ✅ No hardcoded values in templates (all use {{ .Values.X }})

#### T052: Install Helm Chart

```bash
# Install chart with default values
helm install todo-app ./k8s/helm/todo-app

# Expected output:
# NAME: todo-app
# LAST DEPLOYED: Fri Feb 08 10:00:00 2026
# NAMESPACE: default
# STATUS: deployed
# REVISION: 1
# ...

# Verify installation
helm status todo-app

# Expected output:
# NAME: todo-app
# NAMESPACE: default
# STATUS: deployed
# REVISION: 1

# List installed releases
helm list

# Expected output:
# NAME            NAMESPACE       REVISION        UPDATED         STATUS          CHART           APP VERSION
# todo-app        default         1               ...             deployed        todo-app-1.0.0  4.0.0

# Get values used for installation
helm get values todo-app

# Expected: Should show all values (frontend.replicas, backend.replicas, etc.)
```

**Pass Criteria**:
- ✅ Helm install completes successfully
- ✅ Deployment shown in helm list
- ✅ Status shows "deployed"
- ✅ Can retrieve values with helm get values

#### T053: Wait for Pods to Reach Running State

```bash
# Watch pod startup
kubectl get pods -w

# Expected output (stop with Ctrl+C after pods Running):
# NAME                              READY   STATUS              RESTARTS   AGE
# todo-app-frontend-xxxxx           0/1     Pending             0          5s
# todo-app-backend-xxxxx            0/1     ContainerCreating   0          5s
# todo-app-frontend-xxxxx           1/1     Running             0          15s
# todo-app-backend-xxxxx            1/1     Running             0          20s

# Or check final state
kubectl get pods

# Expected output:
# NAME                              READY   STATUS    RESTARTS   AGE
# todo-app-frontend-xxxxx           1/1     Running   0          30s
# todo-app-backend-xxxxx            1/1     Running   0          30s

# Verify all pods are Running (not CrashLoopBackOff, Pending, etc.)
kubectl get pods --no-headers | awk '{print $3}' | sort | uniq

# Expected output should only include:
# Running

# Check pod startup logs
kubectl logs -f deployment/todo-app-backend

# Expected to see:
# Uvicorn running on 0.0.0.0:8000
# Application startup complete

# Check for any errors
kubectl get pods -o wide
kubectl describe pod <any-pod-name>

# Should show:
# Status: Running
# No events with Warning or Error
```

**Pass Criteria**:
- ✅ All pods reach Running state within 60 seconds
- ✅ All pods show 1/1 Ready status
- ✅ No CrashLoopBackOff or ImagePullBackOff states
- ✅ Backend logs show "Application startup complete"
- ✅ Frontend logs show server started

#### T054: Verify Services and Endpoints

```bash
# List services
kubectl get svc

# Expected output:
# NAME                  TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)    AGE
# kubernetes            ClusterIP   10.96.0.1       <none>        443/TCP    XXm
# todo-app-frontend     ClusterIP   10.96.xxx.xxx   <none>        3000/TCP   20s
# todo-app-backend      ClusterIP   10.96.yyy.yyy   <none>        8000/TCP   20s

# Verify endpoints (service → pod mapping)
kubectl get endpoints

# Expected output:
# NAME                  ENDPOINTS                       AGE
# kubernetes            X.X.X.X:6443                    XXm
# todo-app-frontend     10.244.0.2:3000                 20s
# todo-app-backend      10.244.0.3:8000                 20s

# Test service connectivity (from within cluster)
kubectl run -it --rm debug --image=nicolaka/netshoot --restart=Never -- bash

# Inside pod:
curl -v http://todo-app-frontend:3000
curl -v http://todo-app-backend:8000/health

# Expected: Both should return 200 OK

# Exit debug pod
exit
```

**Pass Criteria**:
- ✅ Frontend service created on port 3000
- ✅ Backend service created on port 8000
- ✅ Services have endpoints (pods assigned)
- ✅ Services are reachable within cluster
- ✅ Service DNS names resolve (todo-app-frontend.default.svc.cluster.local)

---

### Section 5: Ingress Configuration & Testing (T055-T057)

#### T055: Verify Ingress Resource Creation

```bash
# List ingress resources
kubectl get ingress

# Expected output:
# NAME       CLASS   HOSTS       ADDRESS         PORTS   AGE
# todo-app   nginx   todo.local  192.168.49.2    80      20s

# Describe ingress for details
kubectl describe ingress todo-app

# Expected output should show:
# Name:             todo-app
# Namespace:        default
# Address:          192.168.49.2 (Minikube IP)
# Default backend:  <none>
# Rules:
#   Host        Path  Backends
#   ----        ----  --------
#   todo.local
#               /api -> todo-app-backend:8000
#               /    -> todo-app-frontend:3000
# Annotations:
#   nginx.ingress.kubernetes.io/rewrite-target: /

# Get ingress YAML
kubectl get ingress todo-app -o yaml

# Expected: Should match k8s/helm/todo-app/templates/ingress.yaml spec
```

**Pass Criteria**:
- ✅ Ingress resource created
- ✅ Ingress class is "nginx"
- ✅ Host is configured as "todo.local"
- ✅ Path rules configured (/api → backend, / → frontend)
- ✅ Address shows Minikube IP

#### T056: Test Ingress Routing (Frontend)

```bash
# Test frontend via ingress
curl -v http://todo.local

# Expected output:
# HTTP/1.1 200 OK
# Server: nginx/X.X.X
# Content-Type: text/html; charset=utf-8
# ...
# (HTML content of Next.js app)

# Test with browser (recommended)
# 1. Open http://todo.local in browser
# 2. Should see login page
# 3. Check browser console (F12) for JavaScript errors
# 4. Verify CSS/images load correctly (no 404s)

# Test health endpoint
curl -v http://todo.local/health

# Expected:
# HTTP/1.1 200 OK
# Content-Type: text/html
# healthy

# Verify frontend responds from correct pod
curl -v -H "Host: todo.local" http://192.168.49.2

# Should route to frontend service
```

**Pass Criteria**:
- ✅ Frontend accessible at http://todo.local
- ✅ HTML content returned (not 404 or 503)
- ✅ No JavaScript console errors in browser
- ✅ CSS and images load (check network tab)
- ✅ Health endpoint returns 200 OK

#### T057: Test Ingress Routing (Backend API)

```bash
# Test backend API health via ingress
curl -v http://todo.local/api/health

# Expected output:
# HTTP/1.1 200 OK
# Content-Type: application/json
# {"status":"healthy"}

# Test backend endpoint without authentication (should return 401)
curl -v http://todo.local/api/tasks

# Expected:
# HTTP/1.1 401 Unauthorized
# {"detail":"Not authenticated"}

# Test backend auth endpoint
curl -v -X POST http://todo.local/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123!",
    "name": "Test User"
  }'

# Expected:
# HTTP/1.1 200 OK
# {"id":1,"email":"test@example.com","access_token":"eyJ..."}

# Test with token
TOKEN=$(curl -s -X POST http://todo.local/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"TestPass123!"}' | jq -r .access_token)

curl -v -H "Authorization: Bearer $TOKEN" http://todo.local/api/tasks

# Expected:
# HTTP/1.1 200 OK
# []  (empty task list initially)

# Verify ingress routing is correct (API prefix)
curl -v http://todo.local/api/health | head -5
# Should show backend response, not frontend 404

# Verify root / goes to frontend
curl -v http://todo.local | head -20 | grep -i "<!DOCTYPE\|html\|<head"
# Should show HTML content
```

**Pass Criteria**:
- ✅ /api/health endpoint returns 200 OK with JSON
- ✅ /api/tasks requires authentication (401 without token)
- ✅ /api/auth/signup works and returns token
- ✅ /api endpoints route to backend service
- ✅ / (root) routes to frontend service
- ✅ Ingress path-based routing working correctly

---

### Section 6: Pod Lifecycle & Resilience Testing (T058-T059)

#### T058: Test Liveness & Readiness Probes

```bash
# Check probe configuration
kubectl get pods -o yaml | grep -A 10 "livenessProbe\|readinessProbe"

# Expected: Should show httpGet probes configured

# Describe pod to see probe status
kubectl describe pod <backend-pod-name> | grep -A 5 "Liveness\|Readiness"

# Expected output:
# Liveness:       http-get http://:8000/health delay=30s timeout=1s period=10s #success=1 #failure=3
# Readiness:      http-get http://:8000/health delay=15s timeout=1s period=5s #success=1 #failure=3

# Verify probes are passing
kubectl get pod <backend-pod-name> -o jsonpath='{.status.conditions[?(@.type=="Ready")].status}'

# Expected output:
# True

# Monitor probe execution
kubectl logs <backend-pod-name> | grep -i "health\|probe"

# Expected: No error logs from health checks

# Test manual health endpoint
kubectl port-forward svc/todo-app-backend 8000:8000 &
curl -v http://localhost:8000/health
kill %1  # Stop port-forward

# Expected: 200 OK with {"status":"healthy"}
```

**Pass Criteria**:
- ✅ Liveness probe configured (30s initial delay)
- ✅ Readiness probe configured (15s initial delay)
- ✅ Pod shows Ready=True
- ✅ Health endpoint responding to probes
- ✅ No probe failures in pod events

#### T059: Test Pod Recovery & Replacement

```bash
# Get list of pods
kubectl get pods

# Record a pod name
OLD_POD=$(kubectl get pods -l app=todo-backend -o jsonpath='{.items[0].metadata.name}')
echo "Watching pod: $OLD_POD"

# Start watching pod status in background
kubectl get pods -w &
WATCH_PID=$!

# Delete a pod to trigger replacement
kubectl delete pod $OLD_POD

# Expected behavior (watch in another terminal):
# NAME                   READY   STATUS    RESTARTS   AGE
# todo-app-backend-xxx   1/1     Terminating  0       2m
# (pod terminates)
# todo-app-backend-yyy   0/1     Pending      0       1s
# (new pod created)
# todo-app-backend-yyy   1/1     Running      0       5s
# (new pod ready)

# Verify service still works after pod replacement
sleep 5
TOKEN="your_token_here"  # From previous tests
curl -H "Authorization: Bearer $TOKEN" http://todo.local/api/tasks

# Expected: 200 OK (service handles pod replacement)

# Verify no data loss (if tasks were created)
curl -H "Authorization: Bearer $TOKEN" http://todo.local/api/tasks | jq length

# Expected: Should return task count (data persists in external DB)

# Stop watching
kill $WATCH_PID

# Check pod restart count
kubectl get pods -l app=todo-backend -o jsonpath='{.items[0].status.containerStatuses[0].restartCount}'

# Expected: Should be 0 (no unexpected restarts)

# Verify new pod has same configuration
NEW_POD=$(kubectl get pods -l app=todo-backend -o jsonpath='{.items[0].metadata.name}')
kubectl describe pod $NEW_POD | grep -E "Image:|RestartPolicy:|Limits:|Requests:"

# Expected: Should match original pod spec (not Recreate policy)
```

**Pass Criteria**:
- ✅ Pod deletion triggers replacement
- ✅ New pod created by deployment controller
- ✅ Service remains accessible during pod transition
- ✅ New pod reaches Running+Ready state
- ✅ No data loss (external database persists)
- ✅ Restart count remains reasonable (no crash loop)

---

## Troubleshooting Kubernetes Issues

### Issue: Minikube Start Fails

```bash
# Solution 1: Delete cluster and restart
minikube delete
minikube start --driver=docker --cpus=4 --memory=8192

# Solution 2: Check Docker daemon
docker ps
docker info | head -10

# Solution 3: Increase Minikube resources
minikube config set memory 8192
minikube config set cpus 4

# Solution 4: Use different driver
minikube delete
minikube start --driver=virtualbox  # or --driver=hyperv (Windows)
```

### Issue: Pods Stuck in Pending

```bash
# Check node resources
kubectl describe nodes

# Check pod events
kubectl describe pod <pod-name>

# Common cause: Insufficient resources
# Solution: Increase Minikube memory/CPU
minikube delete
minikube start --memory=8192 --cpus=4

# Or scale down replicas
kubectl scale deployment todo-app-backend --replicas=1
```

### Issue: CrashLoopBackOff

```bash
# Check logs
kubectl logs <pod-name> --previous  # Previous crashed container
kubectl logs <pod-name>  # Current attempt

# Common causes:
# 1. Database connection error → Check DATABASE_URL in secret
# 2. Missing dependencies → Check requirements.txt
# 3. Port already in use → Check containerPort in deployment
# 4. Health check failing → Check /health endpoint
```

### Issue: Ingress Not Working (503 Service Unavailable)

```bash
# Solution 1: Verify ingress is enabled
minikube addons enable ingress

# Solution 2: Verify ingress controller
kubectl get pods -n ingress-nginx

# Solution 3: Check ingress configuration
kubectl describe ingress todo-app

# Solution 4: Add /etc/hosts entry
MINIKUBE_IP=$(minikube ip)
echo "$MINIKUBE_IP todo.local" | sudo tee -a /etc/hosts

# Solution 5: Test directly via service
kubectl port-forward svc/todo-app-frontend 3000:3000 &
curl http://localhost:3000
kill %1
```

### Issue: Database Connection Error

```bash
# Verify secret exists
kubectl get secret todo-secrets

# Check secret value
kubectl get secret todo-secrets -o jsonpath='{.data.DATABASE_URL}' | base64 -d

# Verify pod can access secret
kubectl exec <pod-name> -- env | grep DATABASE_URL

# Test database connectivity from pod
kubectl exec <pod-name> -- python -c "
import asyncpg
# Connection test code
"

# Common cause: Invalid DATABASE_URL
# Solution: Recreate secret with correct value
kubectl delete secret todo-secrets
kubectl create secret generic todo-secrets \
  --from-literal=DATABASE_URL="postgresql://user:pass@host:5432/db"
```

---

## Summary: Phase 4 Kubernetes Testing Checklist

| Test | Status | Command |
|------|--------|---------|
| T042: Minikube Init | ✅ | `minikube start --cpus=4 --memory=8192` |
| T043: Enable Addons | ✅ | `minikube addons enable ingress` |
| T044: Configure Networking | ✅ | `echo "$IP todo.local" >> /etc/hosts` |
| T045: Verify kubectl | ✅ | `kubectl cluster-info` |
| T046: Docker Env | ✅ | `eval $(minikube docker-env)` |
| T047: Build Frontend | ✅ | `docker build -f docker/frontend.Dockerfile` |
| T048: Build Backend | ✅ | `docker build -f docker/backend.Dockerfile` |
| T049: Create Secret | ✅ | `kubectl create secret generic todo-secrets` |
| T050: Inject Secret | ✅ | `kubectl exec <pod> -- env \| grep DATABASE_URL` |
| T051: Helm Lint | ✅ | `helm lint ./k8s/helm/todo-app` |
| T052: Helm Install | ✅ | `helm install todo-app ./k8s/helm/todo-app` |
| T053: Wait for Pods | ✅ | `kubectl get pods -w` |
| T054: Verify Services | ✅ | `kubectl get svc` |
| T055: Verify Ingress | ✅ | `kubectl get ingress` |
| T056: Test Frontend | ✅ | `curl http://todo.local` |
| T057: Test Backend API | ✅ | `curl http://todo.local/api/health` |
| T058: Liveness Probes | ✅ | `kubectl describe pod <name>` |
| T059: Pod Recovery | ✅ | `kubectl delete pod <name>` |

---

**Phase 4 Kubernetes Testing Complete**: All 18 Minikube deployment tests documented with detailed procedures, expected outputs, and pass criteria.

**Next Phase**: Phase 5 - Chat API Testing (see CHAT_API_TESTING.md) - Test chat endpoints, TodoTools integration, and agent intent parsing.

