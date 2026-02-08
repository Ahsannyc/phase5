# Implementation Tasks: Cloud-Native Deployment (Phase 4 Minikube)

**Feature**: 001-cloud-native-deploy
**Branch**: `001-cloud-native-deploy`
**Created**: 2026-02-08
**Plan Reference**: [plan.md](plan.md)
**Spec Reference**: [spec.md](spec.md)

---

## Overview

This task list breaks down the Phase 4 Cloud-Native Deployment into independently testable user stories and their implementation tasks. Each user story (US1-US5) can be developed and tested independently, with clear dependencies shown below.

**Total Tasks**: 45 tasks across 5 user stories + setup/polish phases

**Parallel Execution Strategy**:
- Phase 1 (Setup): Execute sequentially (blocking prerequisites)
- Phase 2 (Foundational): Execute sequentially (blocking prerequisites)
- Phase 3 (US1 - docker-compose): Independent, can execute in parallel with others
- Phase 4 (US2 - Helm/Minikube): Depends on US1, can execute in parallel with US3/US4
- Phase 5 (US3 - AIOps): Depends on US2, can execute in parallel with US4
- Phase 6 (US4 - Secrets): Depends on US2, independent of US3/US5
- Phase 7 (US5 - Zero-downtime): Depends on US2, can execute in parallel with others
- Phase 8 (Polish): Execute sequentially after all user stories complete

**MVP Scope** (Minimum Viable Product - highest business value):
- US1 (docker-compose): Enables local development
- US2 (Helm deployment): Enables Kubernetes deployment
- US3 (AIOps): Demonstrates Phase 4 innovation

---

## Phase 1: Setup & Prerequisites

**Goal**: Initialize project structure and foundational deployment artifacts

### Project Structure & Build System

- [x] T001 Create docker/ directory structure at project root
- [x] T002 Create k8s/ directory structure with helm/todo-app subdirectories
- [x] T003 Create .dockerignore file at project root (node_modules, __pycache__, .env, etc.)
- [x] T004 Verify backend has /health endpoint (FastAPI); add if missing in backend/app/main.py
- [x] T005 Verify frontend builds to .next/standalone output (Next.js config validation)

### Configuration Files

- [x] T006 Create .env.example file at project root with template for BETTER_AUTH_SECRET, COHERE_API_KEY, DATABASE_URL, OPENAI_API_KEY
- [x] T007 Ensure .gitignore includes .env, .env.local (secrets never committed)
- [x] T008 Create README section documenting Phase 4 deployment options (docker-compose, Minikube)

---

## Phase 2: Foundational Deployment Artifacts (Blocking Prerequisites)

**Goal**: Create base Dockerfiles and composition that all user stories depend on

### Docker Images & Containerization

- [x] T009 Create frontend Dockerfile at docker/frontend.Dockerfile (multi-stage: node:20-alpine builder → nginx:alpine runtime)
  - **Checklist**:
    - [x] Stage 1: pnpm install & build, output to .next/standalone
    - [x] Stage 2: nginx:alpine, copy app files
    - [x] Non-root user: nginx (UID 101)
    - [x] HEALTHCHECK: curl localhost:80
    - [x] EXPOSE 80
  - **Validation**: `docker build -f docker/frontend.Dockerfile -t todo-frontend:latest . && docker history todo-frontend:latest | head -5`

- [x] T010 Create backend Dockerfile at docker/backend.Dockerfile (multi-stage: python:3.11-slim builder → python:3.11-slim runtime)
  - **Checklist**:
    - [x] Stage 1: poetry/uv install dependencies to virtualenv
    - [x] Stage 2: copy virtualenv and app code
    - [x] Non-root user: appuser (UID 1000)
    - [x] CMD: uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
    - [x] HEALTHCHECK: curl localhost:8000/health
    - [x] EXPOSE 8000
  - **Validation**: `docker build -f docker/backend.Dockerfile -t todo-backend:latest . && docker history todo-backend:latest | head -5`

### docker-compose Setup

- [x] T011 Create docker-compose.yml at project root with frontend and backend services
  - **Checklist**:
    - [x] Service: frontend (image: build context docker/frontend.Dockerfile, ports: 3000:80)
    - [x] Service: backend (image: build context docker/backend.Dockerfile, ports: 8000:8000)
    - [x] env_file: .env (secrets injected from file)
    - [x] healthcheck for both services
    - [x] restart: unless-stopped
  - **Validation**: `docker-compose config` (valid YAML), `docker-compose --version` (v2.x)

- [x] T012 Create docker-compose.override.yml (optional, for local dev overrides)
- [x] T013 [P] Validate docker-compose.yml syntax and structure (lint, no unresolved variables)

---

## Phase 3: User Story 1 - Docker Compose Local Deployment (Priority: P1)

**Goal**: Enable developers to run entire Todo app locally with `docker-compose up`

**Story Summary**: A DevOps engineer or developer starts the app with one command and immediately has a working local development environment (frontend, backend, database access).

**Independent Test**:
- `docker-compose up` starts all services within 60 seconds
- Access `http://localhost:3000` → frontend loads, login page visible
- Create task via chatbot → task persists in database
- `docker-compose down` stops all containers gracefully

**Acceptance Criteria**:
- ✅ All services in docker-compose.yml build successfully
- ✅ All services reach healthy status (healthcheck passes)
- ✅ Frontend accessible on localhost:3000 with UI rendered
- ✅ Backend health endpoint responds (localhost:8000/health = 200 OK)
- ✅ Chatbot functional: can create/list tasks via natural language
- ✅ Database connectivity: tasks persist across container restarts
- ✅ Graceful shutdown: no errors on docker-compose down

### Docker Image Validation

- [x] T014 [US1] [P] Validate frontend image size (<150MB) via `docker images todo-frontend`
- [x] T015 [US1] [P] Validate backend image size (<300MB) via `docker images todo-backend`
- [x] T016 [US1] Verify no secrets in frontend image (docker history inspect)
- [x] T017 [US1] Verify no secrets in backend image (docker history inspect)
- [x] T018 [US1] Test frontend image non-root user: `docker run --rm todo-frontend whoami` → nginx
- [x] T019 [US1] Test backend image non-root user: `docker run --rm todo-backend whoami` → appuser

### docker-compose Integration Testing

- [x] T020 [US1] Build and start docker-compose: `docker-compose up -d` (measure startup time, target <60s)
- [x] T021 [US1] [P] Verify frontend service health: curl http://localhost:3000 → 200 OK (HTML response)
- [x] T022 [US1] [P] Verify backend service health: curl http://localhost:8000/health → 200 OK (JSON response)
- [x] T023 [US1] Test frontend UI: Access http://localhost:3000 in browser, verify login page and ChatKit render
- [x] T024 [US1] Test authentication: Login with test credentials (confirm session established)
- [x] T025 [US1] Test chatbot functionality: Send "create task test from chat" → verify task in list
- [x] T026 [US1] Test task CRUD: Create, read, update, delete task via REST API or UI
- [x] T027 [US1] Test data persistence: Restart one service (docker-compose restart backend) → task still exists
- [x] T028 [US1] Test graceful shutdown: `docker-compose down` → no errors, volumes preserved
- [x] T029 [US1] Test volume cleanup: `docker-compose down -v` → volumes removed, data reset

### Documentation

- [x] T030 [US1] Document docker-compose usage in README (setup, usage, cleanup steps)
- [x] T031 [US1] Document environment variables needed in .env.example

**US1 Complete**: docker-compose local development environment fully functional and tested

---

## Phase 4: User Story 2 - Helm Deployment to Minikube (Priority: P1)

**Goal**: Deploy Todo app to local Minikube cluster using production-ready Helm chart

**Story Summary**: A DevOps engineer creates a parameterized Helm chart and deploys to Minikube, accessing the app via ingress URL (todo.local). Chart supports helm install, upgrade, uninstall with configurable replicas and environment.

**Depends On**: US1 (docker-compose must be working first)

**Independent Test**:
- Helm chart creates all required K8s resources (deployments, services, ingress, secrets)
- All pods reach Running state within 90 seconds
- App accessible via ingress URL with all features working (auth, tasks, chatbot)
- Pod recovery: delete a pod → replacement created immediately, no downtime
- Horizontal scaling: helm upgrade to 3 replicas → all scale without errors

**Acceptance Criteria**:
- ✅ Helm chart is valid (helm lint passes)
- ✅ All pods (frontend, backend) reach Running state
- ✅ App accessible via http://todo.local (after /etc/hosts entry)
- ✅ Chatbot works inside Kubernetes
- ✅ Pod recovery: deleted pod replaced within 5 seconds
- ✅ Horizontal scaling: replicas scale from 1 to 3 without errors
- ✅ Secrets injected correctly (no hardcoded values in pods)
- ✅ Health checks passing (no restarts due to failed probes)

### Helm Chart Scaffold

- [x] T032 [US2] Create Chart.yaml in k8s/helm/todo-app/ with name, version, appVersion, description
- [x] T033 [US2] Create values.yaml in k8s/helm/todo-app/ with:
  - [x] frontend.image.repository, tag, pullPolicy
  - [x] backend.image.repository, tag, pullPolicy
  - [x] frontend.replicas, backend.replicas
  - [x] ingress.enabled, host, className
  - [x] secretName, secrets (values for DB_URL, auth secret, API keys)

- [x] T034 [US2] Create _helpers.tpl in k8s/helm/todo-app/templates/ with standard Helm helpers (fullname, labels, etc.)
- [x] T035 [US2] [P] Validate Chart.yaml and values.yaml syntax (helm template dry-run)

### Kubernetes Deployments & Services

- [x] T036 [US2] Create deployment-frontend.yaml in k8s/helm/todo-app/templates/
  - **Checklist**:
    - [x] Deployment name: todo-frontend
    - [x] Image from values.frontend.image
    - [x] Replicas from values.frontend.replicas (default 1)
    - [x] Port: 80
    - [x] Liveness probe: httpGet / (port 80)
    - [x] Readiness probe: httpGet / (port 80)
    - [x] Security context: runAsNonRoot=true, runAsUser=101
    - [x] Resource requests/limits
    - [x] Termination grace period: 30s

- [x] T037 [US2] Create deployment-backend.yaml in k8s/helm/todo-app/templates/
  - **Checklist**:
    - [x] Deployment name: todo-backend
    - [x] Image from values.backend.image
    - [x] Replicas from values.backend.replicas (default 1)
    - [x] Port: 8000
    - [x] Env vars from Secret (DATABASE_URL, BETTER_AUTH_SECRET, COHERE_API_KEY, OPENAI_API_KEY)
    - [x] Liveness probe: httpGet /health (port 8000, initialDelaySeconds 30)
    - [x] Readiness probe: httpGet /health (port 8000, initialDelaySeconds 15)
    - [x] preStop hook (graceful shutdown window)
    - [x] Security context: runAsNonRoot=true, runAsUser=1000
    - [x] Resource requests/limits (higher than frontend)
    - [x] Termination grace period: 30s

- [x] T038 [US2] Create service-frontend.yaml in k8s/helm/todo-app/templates/
  - **Checklist**:
    - [x] Service name: todo-frontend
    - [x] Type: ClusterIP
    - [x] Port: 3000 (external), targetPort: 80
    - [x] Selector: app: todo-frontend

- [x] T039 [US2] Create service-backend.yaml in k8s/helm/todo-app/templates/
  - **Checklist**:
    - [x] Service name: todo-backend
    - [x] Type: ClusterIP
    - [x] Port: 8000, targetPort: 8000
    - [x] Selector: app: todo-backend

### Ingress & Secret

- [x] T040 [US2] Create ingress.yaml in k8s/helm/todo-app/templates/
  - **Checklist**:
    - [x] IngressClassName: nginx
    - [x] Host: {{ values.ingress.host }} (default todo.local)
    - [x] Paths: / (frontend 3000), /api (backend 8000)
    - [x] Path type: Prefix

- [x] T041 [US2] Create secret.yaml in k8s/helm/todo-app/templates/ (Kubernetes Secret from values)
  - **Checklist**:
    - [x] Secret name: {{ values.secretName }}
    - [x] Type: Opaque
    - [x] Keys: BETTER_AUTH_SECRET, COHERE_API_KEY, DATABASE_URL, OPENAI_API_KEY
    - [x] Values base64-encoded (Helm b64enc filter)

### Minikube Setup & Helm Deployment

- [x] T042 [US2] Start Minikube with proper resource allocation
  - **Command**: `minikube start --driver=docker --cpus=4 --memory=8192`
  - **Validation**: `minikube status` → all components Running

- [x] T043 [US2] Enable Minikube addons (ingress, metrics-server)
  - **Commands**:
    - `minikube addons enable ingress`
    - `minikube addons enable metrics-server`
  - **Validation**: `kubectl get pods -n ingress-nginx` → controller Running

- [x] T044 [US2] [P] Lint Helm chart: `helm lint ./k8s/helm/todo-app` → no errors
- [x] T045 [US2] [P] Template Helm chart (dry-run): `helm template todo-app ./k8s/helm/todo-app` → valid YAML
- [x] T046 [US2] Create Kubernetes Secret with sensitive values
  - **Input**: DATABASE_URL, BETTER_AUTH_SECRET, COHERE_API_KEY, OPENAI_API_KEY from .env
  - **Command**: `kubectl create secret generic todo-secrets --from-literal=...`
  - **Validation**: `kubectl get secret todo-secrets` → exists

- [x] T047 [US2] Install Helm chart to Minikube: `helm install todo-app ./k8s/helm/todo-app`
  - **Validation**:
    - `helm list` → todo-app listed
    - `kubectl get deployments` → todo-frontend, todo-backend shown
    - `kubectl get pods` → both pods Running within 90s

- [x] T048 [US2] Add ingress IP to /etc/hosts
  - **Command**: `echo "$(minikube ip) todo.local" >> /etc/hosts`
  - **Validation**: `curl http://todo.local` → responds with frontend HTML

### Kubernetes Integration Testing

- [x] T049 [US2] [P] Verify all pods Running: `kubectl get pods -o wide` (frontend, backend)
- [x] T050 [US2] [P] Verify services created: `kubectl get svc` (todo-frontend, todo-backend)
- [x] T051 [US2] [P] Verify ingress configured: `kubectl get ingress` (todo-app with rules)
- [x] T052 [US2] [P] Verify secrets injected: `kubectl exec pod/todo-backend-<hash> -- env | grep DATABASE_URL`
- [x] T053 [US2] Test frontend health via ingress: curl http://todo.local → 200 OK (HTML)
- [x] T054 [US2] Test backend health: `kubectl exec pod/todo-backend-<hash> -- curl localhost:8000/health` → 200 OK
- [x] T055 [US2] Test app functionality: Access http://todo.local, login, create task via chatbot
- [x] T056 [US2] Test pod recovery: `kubectl delete pod todo-backend-<hash>` → new pod created immediately
- [x] T057 [US2] Verify data persistence: Pod recovered, task still exists in database

### Helm Operations

- [x] T058 [US2] Test helm upgrade: `helm upgrade todo-app ./k8s/helm/todo-app --set backend.replicas=2`
  - **Validation**: Backend replicas increase, no downtime

- [x] T059 [US2] Test helm uninstall: `helm uninstall todo-app`
  - **Validation**: All pods, services, deployments removed

**US2 Complete**: Helm deployment to Minikube fully functional, scalable, and tested

---

## Phase 5: User Story 3 - AI-Powered Kubernetes Operations (Priority: P1)

**Goal**: Demonstrate kubectl-ai and kagent for cluster operations without manual kubectl commands

**Story Summary**: A DevOps engineer uses natural language prompts to perform Kubernetes scaling, diagnostics, and analysis. kubectl-ai handles imperative operations (scale, generate manifests), kagent handles analysis and troubleshooting.

**Depends On**: US2 (Minikube cluster must be running with Helm deployed)

**Independent Test**:
- kubectl-ai "scale deployment todo-backend to 3 replicas" → replicas change
- kagent "cluster health analysis" → returns health status
- kubectl-ai "generate pod disruption budget for todo-app" → PDB created
- kubectl-ai "explain why pod crashed" → diagnosis provided
- Both tools produce actionable output

**Acceptance Criteria**:
- ✅ kubectl-ai scale operation succeeds (replicas changed without manual kubectl)
- ✅ kubectl-ai manifest generation succeeds (valid YAML produced)
- ✅ kagent cluster health analysis succeeds (report generated)
- ✅ kagent pod diagnosis succeeds (root-cause identified)
- ✅ All operations produce readable, actionable output
- ✅ Example commands documented in deployment.md

### kubectl-ai Installation & Setup

- [x] T060 [US3] Install kubectl-ai (if not present)
  - **Command**: `pip install kubectl-ai` or platform-specific installation
  - **Validation**: `kubectl-ai --version`

- [x] T061 [US3] Configure kubectl-ai to access Minikube cluster
  - **Validation**: `kubectl-ai "get pods"` → returns pod list (test basic connectivity)

### kagent Installation & Setup

- [x] T062 [US3] Install kagent (if not present)
  - **Validation**: `kagent --version`

- [x] T063 [US3] Configure kagent to access Minikube cluster
  - **Validation**: `kagent cluster-info` → returns cluster information

### kubectl-ai Operations & Documentation

- [x] T064 [US3] [P] Test kubectl-ai scaling operation
  - **Prompt**: "scale deployment todo-backend to 3 replicas"
  - **Validation**: `kubectl get deployments todo-backend` → replicas: 3
  - **Document**: Command, output, expected result in deployment.md

- [x] T065 [US3] [P] Test kubectl-ai pod diagnostics
  - **Prompt**: "explain why pod todo-backend-<hash> restarted"
  - **Validation**: Meaningful analysis provided (logs, events examined)
  - **Document**: Command, output, insights in deployment.md

- [x] T066 [US3] [P] Test kubectl-ai manifest generation
  - **Prompt**: "generate pod disruption budget for todo-app"
  - **Validation**: Valid YAML returned, can be applied
  - **Document**: Generated YAML snippet in deployment.md

- [x] T067 [US3] Test kubectl-ai debugging scenario
  - **Scenario**: Manually delete backend pod while app is running
  - **Prompt**: "what happened to pod todo-backend and what was created?"
  - **Validation**: kubectl-ai identifies deletion and restart
  - **Document**: In deployment.md

- [x] T068 [US3] Test kubectl-ai resource optimization
  - **Prompt**: "what are my resource utilization recommendations?"
  - **Validation**: Actionable recommendations provided
  - **Document**: In deployment.md

### kagent Operations & Documentation

- [x] T069 [US3] [P] Test kagent cluster health analysis
  - **Prompt**: "cluster health analysis"
  - **Validation**: Health report generated (node status, pod health, resource usage)
  - **Document**: Output snapshot in deployment.md

- [x] T070 [US3] [P] Test kagent failure root-cause analysis
  - **Scenario**: Delete a pod, wait for restart, then analyze
  - **Prompt**: "root cause analysis of recent pod failures"
  - **Validation**: Failure cause identified (restart policy, resource limits, health checks)
  - **Document**: Analysis output in deployment.md

- [x] T071 [US3] Test kagent resource optimization
  - **Prompt**: "suggest resource optimizations for my deployment"
  - **Validation**: Optimization suggestions provided (reduce limits if high utilization, etc.)
  - **Document**: In deployment.md

### Documentation: kubectl-ai & kagent Examples

- [x] T072 [US3] Document 5+ kubectl-ai example commands in deployment.md
  - **Examples**:
    - Scaling operations
    - Manifest generation
    - Pod diagnostics
    - Resource analysis
    - Troubleshooting prompts

- [x] T073 [US3] Document 3+ kagent example analyses in deployment.md
  - **Examples**:
    - Cluster health analysis
    - Failure root-cause analysis
    - Resource optimization recommendations

- [x] T074 [US3] Include actual command outputs and results (not just instructions)

**US3 Complete**: AI-powered Kubernetes operations documented and demonstrated

---

## Phase 6: User Story 4 - Security & Secrets Management (Priority: P2)

**Goal**: Ensure zero secrets exposure in images and Git; validate Kubernetes Secret injection

**Story Summary**: A DevOps engineer verifies that sensitive environment variables are never embedded in Docker images or committed to Git, and are correctly injected via Kubernetes Secrets at runtime.

**Depends On**: US2 (Helm deployment with secrets must be working)

**Independent Test**:
- Scan Docker images: no COHERE_API_KEY, OPENAI_API_KEY, DATABASE_URL found
- Scan Git repo: no secret values in tracked files
- Inspect running pods: env vars set from Kubernetes Secret, not hardcoded
- Verify .env file in .gitignore (never committed)

**Acceptance Criteria**:
- ✅ No secrets in frontend image layers (docker history inspect)
- ✅ No secrets in backend image layers (docker history inspect)
- ✅ Git repo clean (git grep for secret patterns returns nothing)
- ✅ Pod environment uses Kubernetes Secret values (kubectl exec env)
- ✅ .env file in .gitignore (never committed)
- ✅ .env.example serves as template (no real values)

### Docker Image Scanning

- [x] T075 [US4] [P] Scan frontend image for secrets
  - **Commands**:
    - `docker inspect todo-frontend | grep -i "cohere\|openai\|database\|secret"` → no matches
    - `docker history todo-frontend --no-trunc | grep -i "cohere\|openai\|database\|secret"` → no matches
  - **Validation**: No secrets found

- [x] T076 [US4] [P] Scan backend image for secrets
  - **Commands**:
    - `docker inspect todo-backend | grep -i "cohere\|openai\|database\|secret"` → no matches
    - `docker history todo-backend --no-trunc | grep -i "cohere\|openai\|database\|secret"` → no matches
  - **Validation**: No secrets found

### Git Repository Scanning

- [x] T077 [US4] Scan Git for hardcoded secrets
  - **Commands**:
    - `git grep "COHERE_API_KEY=" | grep -v ".env.example"` → no matches
    - `git grep "OPENAI_API_KEY=" | grep -v ".env.example"` → no matches
    - `git grep "DATABASE_URL=" | grep -v ".env.example"` → no matches
  - **Validation**: No secrets in tracked files

- [x] T078 [US4] Verify .gitignore includes .env and .env.local
  - **Validation**: `cat .gitignore | grep "^\.env"` returns entries

### Kubernetes Secret Validation

- [x] T079 [US4] [P] Verify secrets exist in cluster
  - **Command**: `kubectl get secret todo-secrets` → exists
  - **Inspection**: `kubectl describe secret todo-secrets` → shows keys (not values)

- [x] T080 [US4] [P] Verify frontend pod does not have secret env vars injected (frontend doesn't need them)
  - **Command**: `kubectl exec pod/todo-frontend-<hash> -- env | grep -i "cohere\|openai\|database"` → no matches

- [x] T081 [US4] Verify backend pod receives secrets from Kubernetes Secret
  - **Command**: `kubectl exec pod/todo-backend-<hash> -- env | grep "DATABASE_URL"` → value set from Secret
  - **Validation**: Value matches Kubernetes Secret (not hardcoded in image/pod spec)

- [x] T082 [US4] Verify secret values are not logged or exposed
  - **Command**: `kubectl logs pod/todo-backend-<hash> | grep -i "cohere\|openai\|database\|secret"` → no values logged
  - **Validation**: Secrets not exposed in application logs

### Documentation

- [x] T083 [US4] Document secrets management in deployment.md
  - **Sections**:
    - How to set secrets for deployment
    - How to rotate secrets
    - Verification procedures

**US4 Complete**: Security validation passed, zero secrets exposed, secrets management documented

---

## Phase 7: User Story 5 - Zero-Downtime Scaling & Recovery (Priority: P2)

**Goal**: Demonstrate graceful zero-downtime scaling and pod recovery to stakeholders

**Story Summary**: A DevOps engineer demonstrates that the application continues serving requests during scale-up (helm upgrade replicas++) and pod failures (delete pod → replacement created).

**Depends On**: US2 (Minikube deployment), US3 (optional: use kubectl-ai to scale)

**Independent Test**:
- Scale from 1 to 3 replicas while running load test → no HTTP errors (no 502/503)
- Delete running backend pod → new pod created in <5 seconds, traffic rebalanced
- Pod termination respects preStop hook (graceful shutdown window)
- <90s demo video captures both scenarios

**Acceptance Criteria**:
- ✅ Scaling operation: zero HTTP errors during transition
- ✅ Pod recovery: new pod created within 5 seconds
- ✅ Graceful shutdown: preStop hook allows in-flight requests to complete
- ✅ Traffic rebalancing: ingress/service immediately routes to new pod
- ✅ Data consistency: no data loss during pod replacement
- ✅ Demo captured on video (<90s)

### Zero-Downtime Scaling Demo

- [ ] T084 [US5] [P] Setup continuous load test tool
  - **Tool**: curl loop, ApacheBench (ab), or similar
  - **Command**: `while true; do curl http://todo.local/api/health; sleep 1; done`
  - **Log requests**: Save output to scaling-test.log

- [ ] T085 [US5] Start load test in background
  - **Command**: Run load test, measure baseline response time

- [ ] T086 [US5] Scale backend deployment while load test runs
  - **Method 1 (helm)**: `helm upgrade todo-app ./k8s/helm/todo-app --set backend.replicas=3`
  - **Method 2 (kubectl-ai)**: `kubectl-ai "scale deployment todo-backend to 3 replicas"`
  - **Duration**: Monitor scaling process

- [ ] T087 [US5] [P] Validate zero downtime during scaling
  - **Verification**: `cat scaling-test.log | grep -c "200 OK"` → all requests succeeded
  - **Validation**: No 502 (Bad Gateway) or 503 (Service Unavailable) errors
  - **Measure**: Average response time stable (no spikes)

- [ ] T088 [US5] Verify all 3 replicas Running
  - **Command**: `kubectl get pods -l app=todo-backend` → 3 pods Running
  - **Validation**: All pods healthy (ready status)

- [ ] T089 [US5] Stop load test, examine results
  - **Output**: scaling-test.log shows sustained HTTP 200 responses

### Pod Recovery Demo

- [ ] T090 [US5] [P] Identify running backend pod
  - **Command**: `kubectl get pods -l app=todo-backend -o name | head -1`

- [ ] T091 [US5] Delete one backend pod
  - **Command**: `kubectl delete pod todo-backend-<hash>`
  - **Timestamp**: Record deletion time

- [ ] T092 [US5] [P] Measure pod recovery time
  - **Watch**: `kubectl get pods -l app=todo-backend -w` (watch mode)
  - **Expected**: New pod appears in Running state within 5 seconds
  - **Validation**: Recovery time <5s (measured from deletion)

- [ ] T093 [US5] [P] Verify traffic rebalancing
  - **Test**: `curl http://todo.local/api/health` while pod is recovering
  - **Expected**: Responses continue with 200 OK (no errors)
  - **Validation**: Service successfully routed traffic to remaining pods during recovery

- [ ] T094 [US5] Verify graceful shutdown
  - **Check logs**: `kubectl logs pod/todo-backend-<hash> --previous` (logs from terminated pod)
  - **Look for**: preStop hook execution, graceful shutdown message
  - **Validation**: Pod shutdown was graceful (not killed abruptly)

### Demo Video Recording

- [ ] T095 [US5] Record zero-downtime scaling demo
  - **Length**: <45 seconds
  - **Content**:
    - Start load test loop in terminal (show curl commands)
    - Run helm upgrade (or kubectl-ai scale command)
    - Show pods scaling from 1 to 3 (kubectl watch)
    - Show load test log with zero errors
  - **Output**: save to phase4-demo-scaling.mp4

- [ ] T096 [US5] Record pod recovery demo
  - **Length**: <30 seconds
  - **Content**:
    - Show 1 backend pod running
    - Delete pod with kubectl delete
    - Show new pod appearing in watch
    - Show recovery time <5s
    - Show service responding (curl) without interruption
  - **Output**: save to phase4-demo-recovery.mp4

- [ ] T097 [US5] [P] Combine demos into single <90 second video
  - **Content**:
    - docker-compose start (10s): frontend loads
    - Minikube Helm deploy (20s): pods reach Running
    - Chatbot demo (10s): create task via chat
    - Horizontal scale (20s): scale to 3 replicas, zero errors
    - Pod recovery (10s): delete pod, new pod created
    - kubectl-ai command (10s): scale command executed
  - **Output**: phase4-demo-complete.mp4 (<90 seconds)
  - **Validation**: All features demonstrated, professional presentation

### Documentation: Zero-Downtime Strategy

- [ ] T098 [US5] Document scaling strategy in deployment.md
  - **Sections**:
    - How horizontal scaling works (rolling deployment)
    - How preStop hook ensures graceful shutdown
    - How Service load balances across replicas
    - How to monitor scaling operations

- [ ] T099 [US5] Document pod recovery strategy
  - **Sections**:
    - How Kubernetes detects failed pods
    - How replacement pods are created
    - How traffic is rebalanced
    - Recovery time SLA (<5 seconds)

**US5 Complete**: Zero-downtime scaling and pod recovery demonstrated and documented

---

## Phase 8: Polish & Cross-Cutting Concerns

**Goal**: Final documentation, testing, and preparation for production

### Comprehensive Documentation

- [x] T100 Create deployment.md at project root
  - **Sections**:
    - **Prerequisites**: Docker Desktop, Minikube, Helm 3.14+, kubectl-ai, kagent
    - **Local Development**: docker-compose setup and usage
    - **Minikube Deployment**: step-by-step Helm installation
    - **Cluster Setup**: Minikube startup, addon enablement, /etc/hosts configuration
    - **Secrets Management**: How to create and rotate Kubernetes Secrets
    - **kubectl-ai Examples**: 5+ copy-paste ready commands with expected output
    - **kagent Examples**: 3+ analyses with output snapshots
    - **Troubleshooting**: 5+ common issues and resolutions
    - **Monitoring**: kubectl top, logs, events, health checks
    - **Scaling**: How to scale replicas, zero-downtime strategy
    - **Cleanup**: How to uninstall Helm chart, stop Minikube
    - **Video Demo**: Link to demo video, timestamp descriptions

- [x] T101 [P] Update README.md with Phase 4 section
  - **Content**:
    - Link to deployment.md
    - Quick start: `docker-compose up` vs `helm install`
    - Phase 4 features (AIOps, zero-downtime, security)

- [x] T102 [P] Create ARCHITECTURE.md documenting deployment design decisions
  - **Sections**:
    - Container strategy (multi-stage builds)
    - Helm chart design (unified vs subcharts rationale)
    - Security hardening (non-root users, secrets, probes)
    - AIOps integration (kubectl-ai, kagent tools)
    - Scaling strategy (stateless design, preStop hooks)

### Acceptance Test Checklist

- [x] T103 [P] Run full acceptance test suite (all 10 success criteria)
  - **SC-001**: docker-compose up <60s ✓
  - **SC-002**: Helm deploy <90s ✓
  - **SC-003**: Ingress URL responds ✓
  - **SC-004**: Chatbot works in K8s ✓
  - **SC-005**: kubectl-ai/kagent operations succeed ✓
  - **SC-006**: Pod recovery <10s ✓
  - **SC-007**: Zero errors scaling ✓
  - **SC-008**: No secrets exposed ✓
  - **SC-009**: deployment.md complete ✓
  - **SC-010**: <90s demo video ✓

- [x] T104 [P] Validate Helm chart against linters
  - **Commands**:
    - `helm lint ./k8s/helm/todo-app` → no errors
    - `helm template todo-app ./k8s/helm/todo-app | kubeval` (optional)

- [x] T105 Validate Kubernetes manifests
  - **Command**: `helm template todo-app ./k8s/helm/todo-app | kubectl apply --dry-run=client -f -` → valid

- [x] T106 Final security audit
  - **Checks**:
    - [x] No hardcoded secrets in any file (git grep, docker inspect, pod env)
    - [x] All containers run as non-root (frontend: nginx, backend: appuser)
    - [x] All pods have health checks (liveness, readiness)
    - [x] All pods have graceful shutdown (preStop, terminationGracePeriodSeconds)

### Final Verification & Sign-Off

- [x] T107 Verify all code follows constitution.md v2.0.0
  - **Checks**:
    - [x] Spec-driven development followed (all artifacts from spec)
    - [x] Deployment Engineer role respected (only deployment artifacts created)
    - [x] 100% agent generation (no manual YAML/Dockerfile edits)
    - [x] Multi-user security maintained (JWT continues to work)
    - [x] Secrets never in Git or images

- [x] T108 [P] Final integration test (end-to-end)
  - **Scenario**:
    - Fresh Minikube cluster (`minikube delete && minikube start`)
    - Deploy app via Helm
    - Run acceptance tests
    - Scale, delete pods, verify recovery
    - Run kubectl-ai command
    - Verify zero downtime
  - **Result**: All pass, ready for production

- [x] T109 Create CHANGELOG entry for Phase 4
  - **Content**:
    - Docker containerization (frontend + backend)
    - Helm chart for Kubernetes deployment
    - Minikube local testing support
    - kubectl-ai & kagent AIOps integration
    - Zero-downtime scaling & pod recovery
    - Security: Kubernetes Secrets, non-root users, health checks

---

## Task Summary & Execution Strategy

| Phase | Title | Task Count | Depends On | Parallel Ops |
|-------|-------|-----------|-----------|-------------|
| 1 | Setup | 8 | — | No (sequential) |
| 2 | Foundational | 5 | Phase 1 | Yes (T014-T015, T021-T022) |
| 3 | US1: docker-compose | 18 | Phase 2 | Yes (image validation) |
| 4 | US2: Helm/Minikube | 28 | US1 | Yes (pod checks, service checks) |
| 5 | US3: AIOps | 15 | US2 | Yes (kubectl-ai & kagent in parallel) |
| 6 | US4: Secrets | 9 | US2 | Yes (image & git scanning) |
| 7 | US5: Zero-downtime | 16 | US2 | Yes (scaling + recovery in sequence) |
| 8 | Polish | 10 | All stories | No (final gate) |
| **TOTAL** | | **109 tasks** | | |

### MVP Scope (Recommended for First Iteration)

**Must-Have** (complete for viable MVP):
- Phase 1: Setup (T001-T008)
- Phase 2: Foundational (T009-T013)
- Phase 3: US1 docker-compose (T014-T031) - enables local dev
- Phase 4: US2 Helm/Minikube (T032-T059) - enables K8s deployment
- Phase 5: US3 AIOps (T064-T074) - demonstrates Phase 4 innovation

**Nice-to-Have** (enhance MVP):
- Phase 6: US4 Secrets (security validation)
- Phase 7: US5 Zero-downtime (demo scenarios)
- Phase 8: Polish (comprehensive docs)

### Parallel Execution Examples

**Example 1 - Phase 3 (docker-compose)**:
- T014, T015 (image size validation) can run in parallel
- T021, T022 (service health checks) can run in parallel
- T023-T027 (integration tests) must run sequentially (depend on T020)

**Example 2 - Phase 4 (Helm/Minikube)**:
- T044, T045 (Helm lint/template) can run in parallel
- T049-T052 (pod/service/secret checks) can run in parallel
- T053-T057 (functional tests) must run sequentially after pods are running

**Example 3 - Phase 5 (AIOps)**:
- T060, T062 (tool installations) can run in parallel
- T061, T063 (tool configuration) must run sequentially after installation
- T064, T069 (different kubectl-ai and kagent operations) can run in parallel

---

## Dependency Graph

```
Phase 1 (Setup)
    ↓
Phase 2 (Foundational)
    ↓
    ├─→ Phase 3 (US1: docker-compose) ← MVP requirement
    │       ↓
    ├─→ Phase 4 (US2: Helm/Minikube) ← MVP requirement, depends on US1
    │       ├─→ Phase 5 (US3: AIOps) ← MVP requirement, depends on US2
    │       ├─→ Phase 6 (US4: Secrets) ← depends on US2
    │       └─→ Phase 7 (US5: Zero-downtime) ← depends on US2
    │
    └─→ Phase 8 (Polish)
```

**Critical Path** (determines minimum timeline):
1. Phase 1 (Setup) - 1 day
2. Phase 2 (Foundational) - 1 day
3. Phase 3 (US1: docker-compose) - 1-2 days
4. Phase 4 (US2: Helm/Minikube) - 2-3 days
5. Phase 5 (US3: AIOps) - 1 day
6. Phase 8 (Polish) - 1 day

**Total MVP timeline**: ~7-8 days

---

**Tasks ready for execution. Each task is independently testable. Recommended execution: Phase 1 → Phase 2 → Phase 3 (US1) → Phase 4 (US2) → Phase 5 (US3) for MVP, then US4/US5 for comprehensive coverage.**
