# Research & Decision Documentation: Cloud-Native Deployment Phase 4

**Date**: 2026-02-08
**Feature**: 001-cloud-native-deploy
**Purpose**: Resolve architectural unknowns and document rationale for all Phase 4 deployment decisions

---

## R-001: Multi-Stage Dockerfile Best Practices for Node.js + nginx

**Question**: What is the optimal multi-stage Dockerfile pattern for Next.js frontend with nginx serving static output?

**Decision**: Node.js 20-alpine builder → nginx:alpine runtime serving .next/standalone output

**Rationale**:
- Node.js 20-alpine provides pnpm (faster than npm), lightweight base (~150MB)
- nginx:alpine is industry standard for static serving, extremely lightweight (~20MB)
- Next.js standalone output (.next/standalone) is self-contained; no node_modules needed at runtime
- Multi-stage separation: builder uses full Node environment, runtime uses only nginx + app files
- Result: Final image ~100-150MB (vs 500MB+ with node as runtime)

**Alternatives Considered**:
1. **node:20-slim as runtime** (rejected)
   - Would ship entire Node.js runtime to production
   - Larger image (~300MB)
   - Unnecessary dependencies in production

2. **Alpine Python + compiled Node** (rejected)
   - Alpine has limited package ecosystem
   - Added complexity with no real benefit for static serving

3. **Single-stage Node image** (rejected)
   - Cannot separate build artifacts from runtime
   - Includes dev dependencies and build tools in production
   - Much larger image

**Implementation**: Frontend Dockerfile will use node:20-alpine for builder stage, nginx:alpine for runtime stage. COPY .next/standalone from builder to nginx webroot.

**Validation**: Final image size <150MB, HEALTHCHECK curl to port 80 returns 200 OK.

---

## R-002: Multi-Stage Dockerfile Best Practices for Python + uvicorn

**Question**: What is the optimal multi-stage Dockerfile pattern for FastAPI backend with minimal runtime overhead?

**Decision**: python:3.11-slim for both builder and runtime; virtualenv layer copied between stages; uvicorn with 4 workers for concurrency.

**Rationale**:
- python:3.11-slim is ~180MB, significantly smaller than python:3.11 (~900MB)
- Poetry/uv can create virtualenv in builder, copy to runtime (no need to reinstall in runtime stage)
- Slim variant includes gcc and build tools (needed for native dependencies), unlike Alpine
- Alpine Python has known issues with packages requiring native compilation (SQLAlchemy, cryptography)
- uvicorn supports multiple worker processes (gunicorn not needed for basic concurrency)
- Python 3.11 is LTS, stable, widely supported

**Alternatives Considered**:
1. **Python 3.12** (rejected)
   - Newer, but not yet LTS
   - May have compatibility issues with some dependencies (Pydantic, SQLModel)
   - 3.11 is safer for production

2. **Alpine Python** (rejected)
   - Smaller image (~50MB)
   - Incompatibilities with native extension packages (cryptography, psycopg2, SQLAlchemy)
   - Build failures on Alpine very common
   - Time cost of troubleshooting outweighs size savings

3. **python:3.11 (full)** (rejected)
   - 900MB image size
   - Includes unnecessary development tools
   - Not optimized for production

4. **Gunicorn + uvicorn** (rejected)
   - Unnecessary complexity for Phase 4
   - uvicorn --workers 4 sufficient for local development and demos
   - Can add gunicorn in production hardening phase

**Implementation**: Backend Dockerfile will use python:3.11-slim for both stages. Builder stage runs poetry install into virtualenv. Runtime stage copies virtualenv and app code. CMD runs uvicorn with --workers 4.

**Validation**: Final image <200MB, HEALTHCHECK curl to port 8000/health returns 200 OK.

---

## R-003: docker-compose.yml Architecture

**Question**: How should docker-compose.yml be structured for local multi-service Todo app development and testing?

**Decision**: Two services (frontend, backend); external database (Neon); env_file for secrets; healthchecks and restart: unless-stopped.

**Rationale**:
- Mirrors Minikube service architecture (frontend, backend, external DB)
- env_file keeps secrets out of compose.yml itself (prevent accidental commits)
- healthcheck + restart: unless-stopped provides automatic recovery on local machine
- External database (Neon) simplifies Phase 4 scope—no need for postgres service in compose
- Port mapping: frontend:3000 (matches dev expectation), backend:8000 (matches FastAPI default)

**Alternatives Considered**:
1. **Include postgres service in compose** (rejected)
   - Adds complexity to Phase 4
   - Requires database initialization, migrations
   - External Neon is simpler for local testing and matches production design

2. **Hardcode secrets in compose.yml** (rejected)
   - Violates security principle (never commit secrets)
   - Difficult to manage across developers

3. **Using Docker networks explicitly** (rejected)
   - Docker Compose creates implicit bridge network
   - No need to declare network for 2-service app

**Implementation**: docker-compose.yml will define frontend and backend services, read .env file for secrets, include healthchecks referencing container ports, use restart: unless-stopped.

**Validation**: `docker-compose up` starts all services in <60s; frontend responds on :3000, backend on :8000.

---

## R-004: Helm Chart: Unified Chart vs Subcharts

**Question**: Should todo-app be deployed as a single Helm chart or split into subcharts (frontend, backend)?

**Decision**: Single unified Helm chart (todo-app) with two deployments (frontend, backend) and shared values.

**Rationale**:
- Monolithic application (frontend + backend tightly coupled)
- Shared configuration (image pull policy, ingress settings, secret names)
- Single Helm release simplifies upgrade/rollback experience
- Fewer helm install commands for end users
- Easier for local Minikube testing
- Subcharts would add templating complexity without proportional benefit at this scale

**Alternatives Considered**:
1. **Subcharts (frontend chart, backend chart)** (rejected)
   - More modular, but overkill for single app
   - Requires parent chart + 2 subcharts = more files to maintain
   - Helm dependency management adds complexity
   - Useful when frontend/backend can be deployed independently (not this case)

2. **Separate Helm releases** (rejected)
   - `helm install frontend ./k8s/frontend` + `helm install backend ./k8s/backend`
   - Difficult to track app as single unit
   - Separate upgrades risk version mismatches

3. **Kustomize instead of Helm** (rejected)
   - Phase 4 constitution specifies Helm 3+
   - Helm provides templating, version management out-of-box

**Implementation**: Single todo-app chart with Chart.yaml, values.yaml, and templates for both services (deployments, services, ingress, secret, helpers).

**Validation**: `helm install todo-app ./k8s/helm/todo-app` deploys both services; `helm list` shows single todo-app release.

---

## R-005: Kubernetes Secret Management

**Question**: How should sensitive environment variables (API keys, database URL, auth secret) be injected into pods?

**Decision**: Helm Secret template auto-generated from values.yaml; referenced via envFrom.secretRef in Deployments.

**Rationale**:
- Standard Kubernetes pattern (Secret objects, not ConfigMap)
- Secrets never committed to Git; values provided at deployment time
- Helm templating allows `values.yaml` to drive secret generation
- envFrom pattern is cleaner than individual env vars
- Works seamlessly with kubectl-ai secret generation commands

**Alternatives Considered**:
1. **Sealed Secrets / External Secrets Operator** (rejected)
   - Adds significant complexity
   - Requires additional controllers in cluster
   - Overkill for local Minikube development
   - May be useful in production (future phase)

2. **Hard-coded secrets in values.yaml** (rejected)
   - Violates security principle
   - Secrets would be committed to Git

3. **Manual kubectl create secret** (rejected)
   - Not reproducible with code
   - Helm should manage all resources

4. **ConfigMap for all environment variables** (rejected)
   - ConfigMap is not encrypted
   - Cannot store API keys, secrets in ConfigMap

**Implementation**: Create secret.yaml template in Helm that iterates over values and generates Secret resource. Deployments reference `envFrom.secretRef.name: {{ include "todo-app.secretName" . }}`.

**Validation**: `kubectl get secret` shows todo-secrets; `kubectl describe secret todo-secrets` shows keys; `kubectl exec pod -- env | grep COHERE` shows injected value.

---

## R-006: Health Check Endpoints

**Question**: How should pod readiness and liveness probes be configured for frontend and backend?

**Decision**: Backend requires `/health` endpoint (HTTP 200 status); frontend health checked via `curl http://localhost:80` (nginx always responds when healthy).

**Rationale**:
- HTTP GET probes are standard K8s pattern
- `/health` is well-known convention for application health
- Backend can use `/health` to signal readiness (DB connection, dependencies)
- Frontend (nginx) is inherently healthy when listening on port 80
- Avoids exec probes (require shell, slower, fragile)
- Avoids TCP socket probes (less informative about application state)

**Alternatives Considered**:
1. **Custom health endpoint per service** (rejected)
   - `/health` is standard; no need to vary

2. **TCP socket probes** (rejected)
   - Cannot differentiate between "listening but unhealthy" vs "healthy"

3. **Exec probes** (rejected)
   - Require shell in container (adds image size, security surface)
   - Slower than HTTP probes
   - Less reliable

4. **No probes** (rejected)
   - Kubernetes won't know pod is unhealthy
   - Dead pods won't be replaced automatically

**Implementation**:
- Backend Deployment: livenessProbe and readinessProbe with httpGet: path: /health, port: 8000, initialDelaySeconds: 30, periodSeconds: 10
- Frontend Deployment: similar probes on port 80 (nginx always responds)

**Validation**: Deploy pods, `kubectl logs -f deployment/todo-backend` shows health check requests; pod restart log shows probe triggers recovery.

---

## R-007: Minikube Ingress & Service Discovery

**Question**: How should external traffic reach the Todo app from developer machine running Minikube?

**Decision**: nginx ingress controller (via Minikube addon); ClusterIP services for internal routing; hostname todo.local routed to Minikube IP.

**Rationale**:
- nginx ingress is K8s standard, widely supported
- Minikube addon simplifies setup (single command: `minikube addons enable ingress`)
- ClusterIP is default service type; no need for NodePort complexity
- Hostname-based routing (todo.local) is realistic production pattern
- Ingress handles L7 routing (path-based, host-based)

**Alternatives Considered**:
1. **NodePort services** (rejected)
   - Direct port mapping works, but unrealistic
   - Doesn't require ingress controller (not learning K8s patterns)
   - Hard to scale to multiple services

2. **LoadBalancer services** (rejected)
   - Not supported on Minikube (no cloud provider integration)

3. **Port-forward (kubectl port-forward)** (rejected)
   - Works for testing, not for ingress demonstration
   - Doesn't showcase K8s networking

**Implementation**:
- Enable ingress addon: `minikube addons enable ingress`
- Helm chart creates ingress.yaml with `ingressClassName: nginx`, rules for paths `/` (frontend) and `/api/` (backend)
- Add Minikube IP to /etc/hosts: `<minikube-ip> todo.local`

**Validation**: `minikube ip` returns IP; `/etc/hosts` includes entry; `curl -H "Host: todo.local" http://<minikube-ip>` reaches frontend; ingress logs show routing.

---

## R-008: AIOps Integration (kubectl-ai & kagent)

**Question**: Which AI tools should be used for Kubernetes operations, and how should they be demonstrated?

**Decision**: Both kubectl-ai and kagent; kubectl-ai for imperative operations (scale, generate manifests), kagent for analysis (cluster health, root-cause).

**Rationale**:
- Phase 4 constitution mandates kubectl-ai or kagent; using both demonstrates maximum capability
- kubectl-ai excels at generating/executing K8s commands from natural language
- kagent excels at analysis, troubleshooting, recommendations
- Both tools align with hackathon spirit (AI-powered everything)
- Documented examples make integration reproducible

**Alternatives Considered**:
1. **Only kubectl-ai** (rejected)
   - Misses analysis/troubleshooting demonstrations
   - Incomplete AIOps story

2. **Only kagent** (rejected)
   - Misses operational automation (scaling, manifest generation)
   - Less impressive for demo

3. **Manual kubectl commands** (rejected)
   - Violates Phase 4 AIOps requirement
   - Not AI-powered

**Implementation**:
- Document 5 example kubectl-ai prompts and outputs in deployment.md
- Document 2-3 example kagent prompts and analysis in deployment.md
- Include actual command results, not just instructions

**Validation**: deployment.md includes working examples; developer can copy-paste examples and see same results.

---

## R-009: Deployment Order & Testing Strategy

**Question**: In what order should deployment artifacts be created and tested to minimize risk and maximize learning?

**Decision**: Phase 1 (Dockerfiles + docker-compose), Phase 2 (Minikube setup + Helm), Phase 3 (AIOps + docs), Phase 4 (demo video + final validation).

**Rationale**:
- Dockerfiles first: validates containerization logic before K8s complexity
- docker-compose second: validates local dev workflow and app functionality in containers
- Minikube third: validates K8s orchestration works before advanced operations
- Helm chart: validates package management and deployment automation
- AIOps demos last: once infrastructure is stable, showcase operational AI capabilities
- Demo video last: captures polished, working system

**Alternatives Considered**:
1. **Build everything at once** (rejected)
   - Harder to debug (too many variables)
   - If K8s fails, unclear if it's Dockerfile, docker-compose, or Helm issue

2. **Skip docker-compose** (rejected)
   - Misses local development use case
   - Harder to test without Minikube (slower iteration)

3. **Skip testing between phases** (rejected)
   - Risks discovering issues late
   - More work to backtrack and fix

**Implementation**: Task generation will follow this order; each phase has explicit acceptance criteria (docker-compose up passes, Helm deploy passes, etc.).

**Validation**: Each phase has passing tests before proceeding to next phase.

---

## R-010: Documentation Strategy

**Question**: What deployment documentation should be generated?

**Decision**: deployment.md with setup steps, troubleshooting, and AIOps examples; README updates with links to new deployment guide.

**Rationale**:
- deployment.md centralizes all Phase 4 documentation in one place
- Covers: Minikube setup, Helm install, kubectl-ai/kagent examples, troubleshooting common issues
- README updates ensure new users find deployment docs easily
- Executable examples (copy-paste ready) reduce friction

**Alternatives Considered**:
1. **Scattered docs** (rejected)
   - Minikube setup in one file, Helm in another, AIOps in another
   - Hard for users to find comprehensive guide

2. **No examples** (rejected)
   - Users must understand kubectl and Helm deeply
   - Higher barrier to entry

**Implementation**: Generate deployment.md during implementation phase with:
- Prerequisites check
- Step-by-step Minikube setup
- Helm chart explanation
- kubectl-ai example commands and outputs
- kagent example analysis
- Troubleshooting (pod not starting, image pull errors, etc.)
- Rollback procedures

**Validation**: Follow deployment.md step-by-step without errors; app runs at the end.

---

## Summary: All Unknowns Resolved

| # | Topic | Decision | Status |
|---|-------|----------|--------|
| R-001 | Frontend Dockerfile | node:20-alpine → nginx:alpine (multi-stage) | ✅ Resolved |
| R-002 | Backend Dockerfile | python:3.11-slim (multi-stage, virtualenv copy) | ✅ Resolved |
| R-003 | docker-compose.yml | Separate frontend, backend services; external DB; env_file | ✅ Resolved |
| R-004 | Helm Chart | Unified chart with two deployments | ✅ Resolved |
| R-005 | Secrets | Kubernetes Secret objects via Helm template | ✅ Resolved |
| R-006 | Health Checks | HTTP GET probes; `/health` for backend, port 80 for frontend | ✅ Resolved |
| R-007 | Ingress | nginx ingress via Minikube addon; ClusterIP services | ✅ Resolved |
| R-008 | AIOps Tools | Both kubectl-ai and kagent with documented examples | ✅ Resolved |
| R-009 | Deployment Order | Phase 1-4 progression with testing gates | ✅ Resolved |
| R-010 | Documentation | deployment.md with examples and troubleshooting | ✅ Resolved |

**Status**: All research complete. Ready for Phase 1 design and Phase 2 task generation.
