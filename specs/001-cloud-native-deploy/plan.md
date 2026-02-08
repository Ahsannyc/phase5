# Implementation Plan: Cloud-Native Deployment (Phase 4 Minikube)

**Branch**: `001-cloud-native-deploy` | **Date**: 2026-02-08 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-cloud-native-deploy/spec.md`

## Summary

Deploy the complete Todo application (Phase 2 full-stack + Phase 3 AI chatbot) as a production-grade cloud-native Kubernetes application running locally on Minikube. The implementation will create multi-stage Dockerfiles (frontend: Node → nginx, backend: Python → uvicorn), docker-compose.yml for local development, a parameterized Helm 3+ chart for Kubernetes deployment, and demonstrate AIOps capabilities using kubectl-ai and kagent. All artifacts will be 100% agent-generated from this plan with zero manual YAML/Docker editing.

## Technical Context

**Language/Version**: Python 3.11-3.12 (backend), Node.js 20+ (frontend)
**Primary Dependencies**: FastAPI, uvicorn, gunicorn (backend); Next.js, pnpm (frontend); Docker 24+, Minikube, Helm 3.14+, kubectl, kubectl-ai, kagent
**Storage**: Neon PostgreSQL (external, no persistent volumes in Phase 4)
**Testing**: Acceptance tests via docker-compose and Minikube; kubectl get/describe commands for validation
**Target Platform**: Linux containers, Minikube single-node Kubernetes cluster (development), cloud-ready for scaling
**Project Type**: Web application with containerization and Kubernetes orchestration
**Performance Goals**: docker-compose up in <60s; Minikube Helm deploy in <90s; pod recovery <10s
**Constraints**: Multi-stage Dockerfiles for minimal images; non-root users; zero secrets in images/Git; stateless pods; external database only
**Scale/Scope**: Local development + Minikube testing (horizontal scaling demo to 3 replicas); 2 services (frontend, backend)

## Constitution Check

**GATE: Must pass before Phase 0 research.**

| Principle | Requirement | Status | Notes |
|-----------|-------------|--------|-------|
| Spec-Driven Development | All deployment artifacts generated from spec | ✅ PASS | Plan is derived from `/specs/001-cloud-native-deploy/spec.md` |
| Agent Boundaries | Deployment Engineer role for Dockerfiles/Helm/K8s | ✅ PASS | Plan designates Deployment Engineer for all container & K8s artifacts |
| Strict SDD Mandate | No manual code outside Claude Code | ✅ PASS | Plan specifies 100% agent generation; no manual YAML/Dockerfile creation |
| Multi-User Security | JWT verification on every endpoint | ✅ PASS | No changes to auth; Phase 3 JWT security continues in containers |
| No Secrets in Images/Git | All sensitive vars via Kubernetes Secrets | ✅ PASS | Plan includes secret injection via Helm; .env files gitignored |
| Helm Chart Parameterized | values.yaml required; support install/upgrade/uninstall | ✅ PASS | Chart structure includes Chart.yaml, values.yaml, templates; supports helm lifecycle |
| Minikube Focus | Local deployment only; no cloud providers | ✅ PASS | Plan uses Minikube with local Docker images; no ECR/Docker Hub |
| kubectl-ai/kagent Required | At least one meaningful AIOps operation | ✅ PASS | Plan includes kubectl-ai for scaling/debugging and kagent for analysis |
| Non-Root Users | All containers run as non-root | ✅ PASS | Frontend (nginx user), backend (appuser UID 1000) specified |
| Health Checks | Liveness/readiness probes required | ✅ PASS | Plan includes httpGet probes for both services; initialDelaySeconds 30 |

**Gate Result**: ✅ **PASS** – All constitution principles satisfied. Proceed to Phase 0.

---

## Phase 0: Research & Decision Documentation

### Research Tasks (Resolved)

1. **Multi-Stage Dockerfile Best Practices for Node.js + nginx**
   - Decision: Node.js 20-alpine for builder (pnpm install & build), nginx:alpine for runtime (serve static + .next/standalone)
   - Rationale: Alpine images are <50MB; pnpm is faster than npm; nginx serves static efficiently; separation of stages reduces final image size
   - Alternatives considered: node:20-slim (larger image) vs Alpine (chosen for size); node as runtime (less secure, larger)

2. **Multi-Stage Dockerfile Best Practices for Python + uvicorn**
   - Decision: python:3.11-slim for both stages (builder + runtime with virtualenv copy); uvicorn with 4 workers
   - Rationale: python:3.11-slim is <200MB; virtualenv can be copied between stages; uvicorn+gunicorn handles concurrency; no Alpine Python (poetry/uv compatibility issues)
   - Alternatives considered: python:3.12 (newer, not yet stable) vs 3.11 (LTS, chosen); Alpine Python (dependency issues with some packages)

3. **docker-compose.yml Architecture**
   - Decision: Frontend (port 3000), Backend (port 8000) as separate services; env_file: .env; healthcheck & restart: unless-stopped; depends_on: empty (Neon external)
   - Rationale: Mirrors Minikube service design; external DB simplifies compose setup; healthchecks enable auto-restart; env_file keeps secrets out of compose.yml
   - Alternatives considered: docker-compose networks (implicit bridge sufficient for 2 services); explicit depends_on on postgres (rejected - using external Neon)

4. **Helm Chart: Unified Chart vs Subcharts**
   - Decision: Single unified Helm chart (todo-app) with two deployments (frontend, backend), shared values
   - Rationale: Monolithic application; shared values (image pull policy, ingress settings) reduce duplication; simpler for local Minikube; fewer moving parts
   - Alternatives considered: Subcharts for separation (adds complexity; not needed for local dev); separate charts (requires multiple helm install commands)

5. **Kubernetes Secret Management**
   - Decision: Helm Secret template (auto-generated from values.yaml); deployed alongside chart; referenced via envFrom.secretRef
   - Rationale: Standard K8s pattern; secrets never in Git; values.yaml provides override hook; Helm templating generates manifests automatically
   - Alternatives considered: Sealed Secrets (overkill for local Minikube); External Secrets Operator (too complex); hardcoded (violates security)

6. **Health Check Endpoints**
   - Decision: Backend requires `/health` endpoint (HTTP 200); frontend health check via `curl http://localhost:80` (nginx always responds)
   - Rationale: Standard K8s probe pattern; backend can signal readiness; frontend nginx inherently healthy
   - Alternatives considered: TCP socket checks (less informative); exec probes (slower; require shell in image)

7. **Minikube Ingress & Service Discovery**
   - Decision: nginx ingress controller (enabled via minikube addon); ClusterIP services for backend; frontend exposed via ingress with hostname todo.local
   - Rationale: nginx is standard; addon simplifies setup; ClusterIP is default K8s pattern; hostname in /etc/hosts enables browser testing
   - Alternatives considered: NodePort (direct port exposure, less realistic); LoadBalancer (not supported on Minikube)

8. **kubectl-ai & kagent Integration**
   - Decision: Document 5 example prompts in deployment.md; integrate kubectl-ai for manifest generation & scaling, kagent for diagnostics
   - Rationale: Phase 4 mandate requires AIOps demonstration; documented examples reduce friction; both tools are AI-native and align with hackathon spirit
   - Alternatives considered: Manual kubectl commands (violates AIOps requirement); only one tool (reduces demonstration impact)

9. **Deployment Order & Testing Strategy**
   - Decision: Phase 1 (Dockerfiles + docker-compose test), Phase 2 (Minikube setup), Phase 3 (Helm chart + ingress), Phase 4 (AIOps demos + docs)
   - Rationale: Validates containerization before K8s; docker-compose proves functionality with minimal setup; Helm tests K8s orchestration; AIOps last (demonstrates advanced ops)
   - Alternatives considered: Build all at once (harder to debug); skip docker-compose (misses local dev use case)

**Output**: research.md complete (all unknowns resolved). Proceed to Phase 1.

---

## Phase 1: Design & Contracts

### Data Model

**Kubernetes Deployment Model** (no application data changes; Phase 3 schemas reused):

| Entity | Fields | Purpose |
|--------|--------|---------|
| **Pod (Frontend)** | name, image, port (80), livenessProbe, readinessProbe, securityContext | Serves Next.js static UI; health monitored |
| **Pod (Backend)** | name, image, port (8000), livenessProbe, readinessProbe, env (DB_URL, secrets), securityContext | Runs FastAPI app; health monitored; secrets injected |
| **Service (Frontend)** | type: ClusterIP, port: 3000 → 80, selector: app=todo-frontend | Internal service discovery for frontend |
| **Service (Backend)** | type: ClusterIP, port: 8000 → 8000, selector: app=todo-backend | Internal service discovery for backend |
| **Ingress** | host: todo.local, paths: / (frontend), /api/* (backend), className: nginx | External routing via nginx |
| **Secret** | BETTER_AUTH_SECRET, COHERE_API_KEY, DATABASE_URL, OPENAI_API_KEY | Runtime environment injection |
| **ConfigMap** (optional) | Non-sensitive config (API base URLs, feature flags) | Environment configuration |

### API Contracts

No new API contracts; Phase 3 endpoints remain unchanged. Deployment contracts:

**Docker Image Contracts**:
- Frontend image: `todo-frontend:latest` (built locally via docker-compose)
- Backend image: `todo-backend:latest` (built locally via docker-compose)
- Both tagged with `latest` for Minikube; registry: localhost (local Docker daemon)

**Kubernetes Manifest Contracts**:
- Deployment: Must declare replicas, selector, template (spec), probes
- Service: Must declare type, ports, selector
- Ingress: Must declare rules with host + paths, ingressClassName
- Secret: Must declare data (base64) or Helm template

### Project Structure

**Documentation** (feature-specific):
```text
specs/001-cloud-native-deploy/
├── spec.md                 # Feature specification (complete)
├── plan.md                 # This file (/sp.plan output)
├── research.md             # Phase 0 research (this section)
├── data-model.md           # Phase 1 (this section)
├── contracts/              # Phase 1
│   ├── docker-images.md    # Frontend/backend image specifications
│   ├── helm-chart.md       # Helm values schema
│   └── kubernetes.md       # K8s manifest contracts
├── quickstart.md           # Phase 1 (deployment.md will be generated during implementation)
├── checklists/
│   └── requirements.md     # Quality validation (complete)
└── tasks.md                # Phase 2 (/sp.tasks output - NOT created by /sp.plan)
```

**Source Code** (repository root - existing structure extended):
```text
todo-app/
├── frontend/               # Existing Next.js app (no changes)
├── backend/                # Existing FastAPI app (requires /health endpoint)
├── docker/                 # NEW
│   ├── frontend.Dockerfile
│   ├── backend.Dockerfile
│   └── .dockerignore
├── k8s/                    # NEW
│   ├── helm/
│   │   └── todo-app/
│   │       ├── Chart.yaml
│   │       ├── values.yaml
│   │       ├── templates/
│   │       │   ├── _helpers.tpl
│   │       │   ├── deployment-frontend.yaml
│   │       │   ├── deployment-backend.yaml
│   │       │   ├── service-frontend.yaml
│   │       │   ├── service-backend.yaml
│   │       │   ├── ingress.yaml
│   │       │   └── secret.yaml
│   ├── minikube-setup.sh   # Optional helper script
│   └── deployment.md       # Generated during implementation
├── docker-compose.yml      # NEW (local dev orchestration)
├── .dockerignore           # NEW
├── .env.example            # NEW (template for secrets)
└── [existing files]
```

**Structure Decision**: Extended monorepo with new deployment directories (docker/, k8s/) integrated at project root. Reuses existing frontend/, backend/, and specs/ structure. No changes to application code structure; pure infrastructure additions.

## Complexity Tracking

**No constitution violations. No complexity justifications needed.**

---

## Phase 1 (continued): Quickstart & Context

### Quickstart Summary

**Local Development with docker-compose**:
```bash
# 1. Set environment
cp .env.example .env
# (Edit .env with COHERE_API_KEY, OPENAI_API_KEY, DATABASE_URL)

# 2. Build and run
docker-compose up

# 3. Access app
# Frontend: http://localhost:3000
# Backend: http://localhost:8000

# 4. Clean up
docker-compose down
```

**Minikube Deployment with Helm**:
```bash
# 1. Start Minikube
minikube start --driver=docker --cpus=4 --memory=8192
minikube addons enable ingress
minikube addons enable metrics-server

# 2. Set secrets (kubectl-ai generated)
kubectl create secret generic todo-secrets \
  --from-literal=BETTER_AUTH_SECRET=... \
  --from-literal=COHERE_API_KEY=... \
  --from-literal=DATABASE_URL=...

# 3. Deploy via Helm
helm install todo-app ./k8s/helm/todo-app

# 4. Access app
# Ingress: http://todo.local (after adding to /etc/hosts)

# 5. Scale demo
helm upgrade todo-app ./k8s/helm/todo-app --set backend.replicas=3

# 6. Cleanup
helm uninstall todo-app
```

### Artifact Generation Flow

**Dockerfiles**: Generated by Deployment Engineer agent from this plan.
**docker-compose.yml**: Generated from template + plan specifications.
**Helm Chart**: Generated by Helm agent or kubectl-ai from this plan.
**kubectl-ai Prompts**: Documented with examples in deployment.md.

---

## Key Architecture Decisions

| Decision | Choice | Rationale | Trade-offs |
|----------|--------|-----------|-----------|
| Frontend Container | Node → nginx (multi-stage) | Small image size (~150MB), fast serving | Slightly longer build time |
| Backend Container | Python → uvicorn (multi-stage) | Minimal overhead, async support | No synchronous ASGI runners |
| Local Orchestration | docker-compose + Minikube | Matches production K8s, easy local testing | Requires Docker Desktop + Minikube |
| Helm Chart | Single unified chart | Simpler for small app, shared values | Subcharts would be more modular (not needed yet) |
| Secrets | K8s Secret objects | Standard cloud-native pattern | Requires Minikube for testing |
| Ingress | nginx | Standard, widely supported | NodePort alternative less realistic |
| Database | External Neon | Simplifies Phase 4 scope | Requires external DB setup |
| AIOps Tools | kubectl-ai + kagent | Both needed for Phase 4 mandate | Two tools to learn/document |

---

## Implementation Roadmap

**Phase 1 (Dockerfiles & docker-compose)** → Task Group 1
- Create .dockerignore
- Frontend Dockerfile (multi-stage, nginx)
- Backend Dockerfile (multi-stage, uvicorn)
- docker-compose.yml
- Test: `docker-compose up` → app runs locally

**Phase 2 (Minikube & Helm Chart)** → Task Group 2
- Minikube setup script or documentation
- Helm Chart skeleton (Chart.yaml, values.yaml)
- Helm templates (deployments, services, ingress, secrets, helpers)
- Test: `helm install` → app runs on Minikube

**Phase 3 (AIOps & Documentation)** → Task Group 3
- kubectl-ai prompt examples (documented with outputs)
- kagent analysis examples (documented with outputs)
- deployment.md (setup, troubleshooting, commands)
- README updates (new deployment instructions)
- Test: kubectl-ai scale, kagent diagnostics work

**Phase 4 (Demo & Validation)** → Task Group 4
- Zero-downtime scaling demo
- Pod recovery demo
- Record <90s video
- Full validation against all success criteria

---

## Constitution Compliance (Re-check Post-Design)

| Principle | Compliance | Evidence |
|-----------|-----------|----------|
| Spec-Driven | ✅ PASS | All artifacts derived from spec.md |
| Deployment Engineer Role | ✅ PASS | Deployment Engineer creates all deployment artifacts |
| 100% Agent Generation | ✅ PASS | Plan designates all artifact generation to agents (no manual YAML) |
| No Manual Code | ✅ PASS | All Dockerfiles, Helm, docker-compose generated; no manual edits allowed |
| Multi-User Security | ✅ PASS | Phase 3 JWT security preserved; no changes to auth endpoints |
| Secret Management | ✅ PASS | Secrets via K8s Secret objects; never in images or Git |
| Helm Parameterization | ✅ PASS | values.yaml supports image tags, replicas, secrets, ingress configuration |
| Minikube Focus | ✅ PASS | No cloud provider references; local Docker images only |
| kubectl-ai/kagent Required | ✅ PASS | Plan includes documentation and demonstration of both tools |
| Non-Root Users | ✅ PASS | Frontend (nginx user), backend (appuser UID 1000) specified |
| Health Checks | ✅ PASS | Probes defined for both services; initial delay 30s, period 10s |

**Gate Result**: ✅ **PASS** – Phase 1 design maintains full compliance. Ready for Phase 2 task generation.

---

## Next Steps

**Ready for**: `/sp.tasks` to generate implementation tasks based on this plan.

**Deliverables Expected from /sp.tasks**:
1. Task breakdown for Dockerfiles (frontend, backend, .dockerignore)
2. Task for docker-compose.yml creation and testing
3. Task for Helm chart scaffold and template generation
4. Tasks for kubectl-ai example documentation
5. Task for deployment.md and README updates
6. Task for demo video recording and final validation

**Success Criteria Validation** (will be verified during implementation):
- ✅ SC-001: docker-compose up in <60s → validated during docker-compose testing task
- ✅ SC-002: Helm deployment in <90s → validated during Minikube testing task
- ✅ SC-003: App accessible via ingress → validated during ingress testing task
- ✅ SC-004: Chatbot works in K8s → validated during functional testing task
- ✅ SC-005: kubectl-ai/kagent operations succeed → validated during AIOps task
- ✅ SC-006: Pod recovery <10s → validated during recovery demo task
- ✅ SC-007: Zero errors during scale → validated during scaling demo task
- ✅ SC-008: Zero secrets exposed → validated during security audit task
- ✅ SC-009: deployment.md complete → validated during documentation task
- ✅ SC-010: <90s demo video → validated during video recording task

---

**This plan is complete and ready for task decomposition via `/sp.tasks`.**
