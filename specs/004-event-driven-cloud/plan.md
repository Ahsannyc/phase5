# Implementation Plan: Phase 5 – Event-Driven & Cloud Deployment

**Branch**: `004-event-driven-cloud` | **Date**: 2026-02-09 | **Spec**: `/specs/004-event-driven-cloud/spec.md`

**Input**: Feature specification from `/specs/004-event-driven-cloud/spec.md` (6 user stories, 39 functional requirements, 14 success criteria)

---

## Summary

Complete Phase V by implementing event-driven architecture (Kafka + Dapr) and deploying the Todo application to Oracle Kubernetes Engine (OKE) with CI/CD, monitoring, and observability. This plan covers Parts A (remaining), B (local Minikube), and C (cloud production). Foundation: Phase 2-4 fully implemented (frontend, backend, chatbot). Phase 5 Part A features (priorities, tags, search, filter, sort, recurring, due dates) already complete and working.

---

## Technical Context

**Language/Version**: Python 3.11 (backend), TypeScript/Next.js 16+ (frontend), Go/Python (Dapr services)

**Primary Dependencies**:
- Backend: FastAPI 0.104+, SQLModel 0.0.14+, Alembic 1.12+, Neon PostgreSQL (external)
- Frontend: Next.js 16+, TypeScript 5+, Tailwind CSS, Better Auth
- Dapr: Dapr 1.14+, Dapr Python SDK
- Kafka: Strimzi Operator (self-hosted) or Redpanda Cloud (managed)
- Kubernetes: Minikube 1.30+ (local), Oracle OKE 1.27+ (cloud)
- Monitoring: Prometheus 2.45+, Grafana 10.0+, Loki 2.9+
- CI/CD: GitHub Actions, Docker 24+, Helm 3.12+

**Storage**: PostgreSQL/Neon (tasks, users, conversations, notifications, audit logs); Dapr State Store (persistent state); Kafka (event streaming)

**Testing**: pytest (backend), jest (frontend), integration tests via `curl` and `helm test`

**Target Platform**: Oracle Kubernetes Engine (OKE) free tier (4 OCPUs, 24GB RAM); Minikube for local validation

**Project Type**: Full-stack web application with event-driven backend and Kubernetes orchestration

**Performance Goals**:
- Minikube deployment: pods Ready in <5 minutes
- OKE deployment: pods Ready in <5 minutes
- Event latency: <5 seconds (Kafka → consumer processing)
- Reminder delivery: 98% within 5 minutes of due time
- Zero-downtime updates: rolling deployment with <1s request disruption
- Concurrent users: 1000 without degradation

**Constraints**:
- No secrets in Git or Docker images (use Kubernetes Secrets, Oracle Vault, external-secrets operator)
- All Kubernetes YAML generated via Helm (no manual kubectl apply)
- Multi-user isolation: all queries filter by user_id from JWT
- Stateless pods: external Neon DB + Dapr state store
- Production security: NetworkPolicy (deny-all default), RBAC (least privilege), non-root containers, read-only root filesystem where possible
- No custom CRDs or operators (use standard Kubernetes resources)

**Scale/Scope**:
- Multi-service deployment: frontend (Next.js), backend (FastAPI), optionally notification/audit services
- 10,000+ users with 100,000+ tasks
- Kafka: 3 topics (task-events, reminders, task-updates)
- Dapr: 5 building blocks (Pub/Sub, State, Bindings, Secrets, Service Invocation)
- Monitoring: Prometheus scrape every 15s, Grafana dashboards (7-10 pre-built), Loki log indexing, AlertManager rules (10+ alerts)

---

## Constitution Check

**GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.**

### Spec-Driven Development (NON-NEGOTIABLE) ✅ PASS
- **Requirement**: All code/manifests generated from approved specs
- **Status**: Specification approved (spec.md in `/specs/004-event-driven-cloud/spec.md`)
- **Implementation**: All agents will follow spec precisely; no manual coding outside Claude Code
- **Verification**: Every agent will confirm spec approval before generating code

### Strict Agent Boundaries ✅ PASS
- **Requirement**: Each agent has defined role; no cross-contamination
- **Scope**: Phase 5 involves 12+ specialized agents:
  - Dapr Specialist (sidecars, components)
  - Dapr Kafka Engineer (Kafka producers/consumers via Dapr)
  - Event-Driven Architect (event flows, schemas)
  - Cloud Deployment Engineer (OKE provisioning, Helm deployment)
  - Blueprint GitOps Engineer (Helm charts, ArgoCD)
  - Observability AIOps Agent (Prometheus, Grafana, Loki)
  - K8s Production Hardening (NetworkPolicy, RBAC, security)
  - Integration Tester (E2E validation)
- **Verification**: Each agent will operate only within scope; no backend engineer writing Dapr components, etc.

### Multi-User Security Enforcement ✅ PASS
- **Requirement**: All operations filter by user_id from JWT
- **Implementation**: Existing Phase 2-3 code already enforces this; Part A features inherit this
- **Verification**: Every query includes `WHERE user_id = current_user_id`; tests confirm User A cannot see User B's data

### Spec Approval Requirement ✅ PASS
- **Requirement**: Coding agents must verify spec approval before implementation
- **Implementation**: Spec approved and committed to `004-event-driven-cloud` branch
- **Verification**: Agents will confirm: "Are specs (Dapr components + Helm charts + GitHub Actions + Prometheus config) approved?" → YES

### No Manual Coding Outside Claude Code ✅ PASS
- **Requirement**: All artifacts agent-generated
- **Implementation**: This plan ensures all YAML, Dockerfiles, Helm charts, CI/CD workflows are generated by agents
- **Verification**: No manual `kubectl apply`, no hand-edited charts, no script editing

### Phase 5 Part B & C Independence from Part A ✅ PASS
- **Requirement**: Parts B & C can run independently of Part A features
- **Clarification**: Part A (priorities, tags, etc.) already complete. Parts B & C add event-driven architecture and cloud deployment on top of completed Part A
- **Verification**: Event-driven system works even if Part A features disabled; cloud deployment works even if events disabled (for Part B validation)

---

## Project Structure

### Documentation (this feature)

```text
specs/004-event-driven-cloud/
├── spec.md                      # ✅ Feature specification (user stories, requirements)
├── plan.md                      # ← THIS FILE (architecture decisions, roadmap)
├── research.md                  # ← Phase 0 output (research findings, decisions)
├── data-model.md                # ← Phase 1 output (Kafka topics, event schemas, Dapr components)
├── quickstart.md                # ← Phase 1 output (local setup, deployment walkthroughs)
├── checklists/
│   └── requirements.md          # ✅ Quality validation (13 items passed)
└── contracts/
    ├── kafka-events.md          # Event schema definitions
    ├── dapr-components.yaml     # Dapr component specs
    └── helm-chart-values.yaml   # Helm parameterization contract
```

### Source Code (repository root - additions only)

```text
# Containerization
docker/
├── frontend.Dockerfile         # Multi-stage: Next.js 16 → nginx
├── backend.Dockerfile          # Multi-stage: FastAPI → uvicorn
└── .dockerignore

# Kubernetes & Helm
k8s/
├── helm/
│   └── todo-app/
│       ├── Chart.yaml           # Helm chart metadata (name, version, description)
│       ├── values.yaml          # Default values (image tags, replicas, resources, config)
│       ├── values-minikube.yaml # Minikube overrides (fewer replicas, local image registry)
│       ├── values-oke.yaml      # OKE overrides (Oracle Container Registry, 3 replicas, resources)
│       ├── templates/
│       │   ├── deployment-frontend.yaml
│       │   ├── deployment-backend.yaml
│       │   ├── service-frontend.yaml
│       │   ├── service-backend.yaml
│       │   ├── ingress.yaml     # Ingress (TLS via cert-manager or OCI)
│       │   ├── configmap.yaml   # Non-sensitive config (API URLs, ChatKit keys)
│       │   ├── secret.yaml      # Secret references (managed externally)
│       │   ├── serviceaccount.yaml
│       │   ├── rbac.yaml        # Role, RoleBinding (least-privilege)
│       │   ├── networkpolicy.yaml # SecurityPolicy (deny-all default)
│       │   ├── _helpers.tpl     # Helper functions (image names, labels, etc.)
│       │   └── NOTES.txt        # Post-install instructions
│       └── tests/
│           └── test-deployment.yaml # helm test spec
│
├── dapr/
│   ├── components/
│   │   ├── kafka-pubsub.yaml    # Dapr Pub/Sub (Kafka backing)
│   │   ├── postgresql-state.yaml # Dapr State Store (PostgreSQL backing)
│   │   ├── cron-binding.yaml    # Dapr Bindings (cron for reminders)
│   │   └── kubernetes-secrets.yaml # Dapr Secrets (Kubernetes backing)
│   └── config/
│       └── dapr-config.yaml     # Global Dapr configuration
│
├── kafka/
│   └── strimzi/
│       ├── namespace.yaml       # kafka namespace
│       ├── strimzi-operator.yaml # Strimzi operator deployment
│       └── kafka-cluster.yaml   # Kafka cluster (1-3 brokers)
│
├── monitoring/
│   ├── prometheus/
│   │   ├── deployment.yaml
│   │   ├── configmap.yaml       # prometheus.yml scrape config
│   │   └── service.yaml
│   ├── grafana/
│   │   ├── deployment.yaml
│   │   ├── configmap.yaml       # Grafana dashboards (JSON)
│   │   └── service.yaml
│   └── loki/
│       ├── deployment.yaml
│       ├── configmap.yaml       # Loki config
│       └── service.yaml
│
├── cert-manager/
│   └── clusterissuer.yaml       # Let's Encrypt issuer for TLS
│
└── deployment.md                # Deployment guide (OKE setup, Helm commands, troubleshooting)

# CI/CD
.github/workflows/
└── deploy-oke.yaml             # GitHub Actions (build → test → push → deploy)

# Configuration
.dockerignore                   # Docker build context excludes
docker-compose-extended.yaml    # Extended for event-driven (Kafka, Dapr, monitoring)
```

**Structure Decision**:
- Helm chart as single package (`k8s/helm/todo-app/`) parameterized for multiple environments (Minikube, OKE)
- Dapr components in separate directory (`k8s/dapr/components/`) for clarity
- Kafka deployed via Strimzi operator (free, self-hosted) on both Minikube and OKE
- Monitoring stack (Prometheus + Grafana + Loki) deployed to cluster for observability
- GitHub Actions workflow builds images, pushes to registry, and deploys via Helm

---

## Phase 0: Research & Unknowns Resolution

**Duration**: ~2-3 hours (concurrent research tasks)

### Research Tasks

1. **Dapr Integration Strategy** (Dapr Specialist)
   - **Unknown**: How to properly configure Dapr sidecars on Minikube vs OKE?
   - **Research**: Dapr sidecar injection annotations, component communication patterns, state store configuration
   - **Outcome**: Document in research.md with Dapr 1.14+ best practices

2. **Kafka Topic Design & Partitioning** (Dapr Kafka Engineer)
   - **Unknown**: How many partitions, replicas, and retention for task-events, reminders, task-updates topics?
   - **Research**: Kafka best practices for event streaming, consumer group management, offset tracking
   - **Outcome**: Document topic schemas and partitioning strategy

3. **Oracle OKE Free Tier Limitations** (Cloud Deployment Engineer)
   - **Unknown**: What are the constraints of OKE free tier (4 OCPU, 24GB)? Can it run Kafka, Prometheus, Grafana?
   - **Research**: OKE documentation, resource requirements for components, networking setup
   - **Outcome**: Document OKE setup procedure and resource allocation strategy

4. **GitHub Actions to OKE Authentication** (CI/CD Engineer)
   - **Unknown**: How to authenticate GitHub Actions runner to OKE cluster securely?
   - **Research**: OKE kubeconfig generation, GitHub Actions secrets, IAM roles vs credentials
   - **Outcome**: Document authentication pattern in CI/CD workflow

5. **External-Secrets Operator Setup** (Observability AIOps Agent)
   - **Unknown**: How to integrate external-secrets operator with Kubernetes Secrets?
   - **Research**: external-secrets provider patterns, Oracle Vault integration
   - **Outcome**: Document secrets management strategy

6. **Helm Chart Parameterization** (Blueprint GitOps Engineer)
   - **Unknown**: What values should be parameterized for multi-environment deployment?
   - **Research**: Helm best practices, values inheritance, template functions
   - **Outcome**: Document values-minikube.yaml and values-oke.yaml overrides

7. **Production Kubernetes Security** (K8s Production Hardening)
   - **Unknown**: What NetworkPolicy, RBAC, and Pod Security Admission rules are needed?
   - **Research**: K8s security best practices, least-privilege configuration
   - **Outcome**: Document security policies in data-model.md

8. **Prometheus Metrics Collection** (Observability AIOps Agent)
   - **Unknown**: What metrics should FastAPI backend expose? How to configure scrape intervals?
   - **Research**: Prometheus Python libraries, common Todo app metrics
   - **Outcome**: Document metrics scrape config and Grafana dashboard structure

### Phase 0 Output

**File**: `specs/004-event-driven-cloud/research.md` (~100 lines)

```markdown
# Phase 5 Event-Driven & Cloud Research Findings

## Decision 1: Dapr Sidecar Injection
**Choice**: Kubernetes annotations (dapr.io/enabled: "true") for automatic sidecar injection
**Rationale**: Simplest approach; Dapr control plane handles injection
**Alternatives**: Manual sidecar containers (not recommended)

## Decision 2: Kafka Partitioning
**Choice**: task-events (3 partitions), reminders (1 partition), task-updates (3 partitions)
**Rationale**: 3 partitions enables parallel consumption; reminders use 1 for ordering
**Alternatives**: Single partition (simpler but slower)

## Decision 3: OKE Resource Allocation
**Choice**: Frontend (250m CPU, 256Mi), Backend (500m CPU, 512Mi), Kafka (2 CPU, 4Gi)
**Rationale**: Free tier 4 OCPU total; allocation leaves room for monitoring stack
**Alternatives**: Reduce to 1 Kafka broker (higher risk)

[... additional 5 decisions documented ...]
```

---

## Phase 1: Design & Contracts

**Duration**: ~4-6 hours (can be parallelized with Phase 0)

### Phase 1a: Data Model & Event Schemas

**File**: `specs/004-event-driven-cloud/data-model.md` (~150 lines)

```markdown
# Phase 5 Data Model: Event-Driven Architecture

## Kafka Topics & Event Schemas

### Topic 1: task-events
**Purpose**: All task CRUD operations
**Consumers**: Audit service, reminder service, real-time sync
**Schema**:
```json
{
  "event_id": "uuid",           // Idempotency key
  "event_type": "task_created | task_updated | task_completed | task_deleted",
  "task_id": "uuid",
  "user_id": 123,
  "timestamp": "2026-02-09T12:34:56Z",
  "task_data": { /* complete task object */ },
  "old_data": { /* for update/delete, previous state */ }
}
```

### Topic 2: reminders
**Purpose**: Due-date reminder events triggered by cron
**Consumers**: Notification service
**Schema**:
```json
{
  "event_id": "uuid",
  "task_id": "uuid",
  "user_id": 123,
  "reminder_time": "2026-02-09T14:00:00Z",
  "notification_type": "due_date | reminder"
}
```

### Topic 3: task-updates
**Purpose**: Real-time task state changes for frontend sync
**Consumers**: WebSocket service (future), frontend long-polling
**Schema**: Same as task-events task_data

## Dapr Components

### PubSub: kafka-pubsub
**Type**: pubsub.kafka
**Metadata**:
- brokers: ["localhost:9092"] (Minikube) or managed Kafka endpoint (OKE)
- consumer_group: "todo-app"
- auth_required: false (local), true (production)

### State Store: postgresql-state
**Type**: state.postgresql
**Metadata**:
- connection_string: "postgresql://user:pass@neon.example.com/todo"
- table_name: "dapr_state"

### Bindings: cron-binding
**Type**: bindings.cron
**Metadata**:
- expression: "@every 5m" (check reminders every 5 minutes)
- direction: "input" (trigger incoming requests)

### Secrets: kubernetes-secrets
**Type**: secretstores.kubernetes
**Metadata**:
- auth: "pod" (service account auth)
- namespace: "default"
```

### Phase 1b: API & Dapr Service Contracts

**File**: `specs/004-event-driven-cloud/contracts/kafka-events.md` (~100 lines)

Documents:
- Event schema definitions (JSON)
- Kafka topic naming and partitioning
- Dapr service invocation endpoints
- Error handling and dead-letter queue patterns

### Phase 1c: Helm Chart Structure

**File**: `specs/004-event-driven-cloud/contracts/helm-chart-values.yaml` (~150 lines)

Documents:
- values.yaml default parameters (image tags, replicas, resources)
- values-minikube.yaml overrides (nodePort services, fewer replicas)
- values-oke.yaml overrides (LoadBalancer, Ingress, 3+ replicas)
- Parameterization contract (what values must be externalized)

### Phase 1d: Quickstart Guide

**File**: `specs/004-event-driven-cloud/quickstart.md` (~200 lines)

```markdown
# Phase 5 Event-Driven & Cloud Quickstart

## Local Setup (Minikube + Dapr + Kafka)

### Prerequisites
- Minikube 1.30+ with 4+ CPUs, 8GB+ RAM
- kubectl 1.27+
- Helm 3.12+
- Docker 24+

### Step 1: Start Minikube
\`\`\`bash
minikube start --cpus=4 --memory=8192 --disk-size=50g
minikube addons enable ingress metrics-server
\`\`\`

### Step 2: Install Dapr
\`\`\`bash
dapr init -k --runtime-version 1.14
\`\`\`

### Step 3: Install Kafka (Strimzi)
\`\`\`bash
helm repo add strimzi https://strimzi.io/charts
helm install strimzi-operator strimzi/strimzi-kafka-operator -n kafka --create-namespace
helm install kafka-cluster ./k8s/kafka/strimzi-kafka-cluster.yaml -n kafka
\`\`\`

### Step 4: Deploy Todo App
\`\`\`bash
helm install todo ./k8s/helm/todo-app -f ./k8s/helm/todo-app/values-minikube.yaml
\`\`\`

### Step 5: Verify Deployment
\`\`\`bash
kubectl get pods -n default
dapr status -k
kubectl port-forward svc/todo-frontend 3000:3000 &
kubectl port-forward svc/todo-backend 8000:8000 &
\`\`\`

## Cloud Setup (Oracle OKE)

### Prerequisites
- Oracle account with free tier eligibility
- OCI CLI configured with credentials
- kubectl context configured to OKE cluster

### Step 1: Provision OKE Cluster
[Instructions for OKE provisioning via OCI Console or CLI]

### Step 2: Deploy Via Helm
\`\`\`bash
helm install todo ./k8s/helm/todo-app -f ./k8s/helm/todo-app/values-oke.yaml
\`\`\`

[... additional setup steps ...]
```

### Phase 1 Output Files

1. `specs/004-event-driven-cloud/data-model.md` - Event schemas, Dapr components, database state
2. `specs/004-event-driven-cloud/contracts/kafka-events.md` - Event contract definitions
3. `specs/004-event-driven-cloud/contracts/helm-chart-values.yaml` - Helm parameterization spec
4. `specs/004-event-driven-cloud/quickstart.md` - Setup walkthroughs for Minikube and OKE
5. `specs/004-event-driven-cloud/research.md` - Phase 0 research findings and decisions

---

## Phase 2: Implementation Roadmap (Tasks Breakdown)

**Duration**: ~40-60 hours across 8+ specialized agents (parallelizable)

### Implementation Stages

**Stage 1: Dapr & Kafka Foundation** (8-12 hours, ~20 tasks)
- Create Dapr component YAML files (Pub/Sub, State, Bindings, Secrets)
- Create Kafka cluster deployment (Strimzi)
- Define Kafka topics and event schemas
- Create Docker Compose with Dapr + Kafka for local testing
- **Owner**: Dapr Specialist + Dapr Kafka Engineer
- **Blocker**: None; can start immediately after Phase 1 research complete

**Stage 2: Backend Event Integration** (10-15 hours, ~20 tasks)
- Update backend API to publish task-events, reminders, task-updates
- Implement Dapr HTTP sidecar calls for event publishing
- Create audit service consumer for task-events
- Create reminder service consumer for reminders topic
- Add error handling and dead-letter queue logic
- Test end-to-end event flow locally
- **Owner**: Backend Engineer + Dapr Kafka Engineer
- **Blocker**: Stage 1 complete; requires Kafka running

**Stage 3: Helm Chart & Kubernetes Manifests** (12-18 hours, ~25 tasks)
- Create Helm chart structure (Chart.yaml, values.yaml, templates)
- Generate Kubernetes manifests (Deployment, Service, Ingress, ConfigMap, Secret, RBAC, NetworkPolicy, PodSecurityPolicy)
- Create multi-environment values files (minikube, oke)
- Add health probes (liveness, readiness, startup)
- Add Dapr sidecar injection annotations
- Create Helm tests
- **Owner**: Blueprint GitOps Engineer + K8s Production Hardening
- **Blocker**: Stage 1 complete; can run in parallel with Stage 2

**Stage 4: Docker Multi-Stage Builds** (4-6 hours, ~5 tasks)
- Create frontend.Dockerfile (Next.js 16 → nginx)
- Create backend.Dockerfile (FastAPI → uvicorn)
- Optimize image sizes (multi-stage, minimal base images)
- Test images locally with docker-compose
- **Owner**: Cloud Deployment Engineer
- **Blocker**: None; can start immediately

**Stage 5: CI/CD Pipeline (GitHub Actions)** (6-10 hours, ~15 tasks)
- Create GitHub Actions workflow (.github/workflows/deploy-oke.yaml)
- Implement build step (docker build frontend, docker build backend)
- Implement test step (pytest backend, jest frontend)
- Implement push step (authenticate to container registry, push images)
- Implement deploy step (authenticate to OKE, helm upgrade/install)
- Add smoke tests (curl health endpoints)
- Add rollback capability
- **Owner**: Cloud Deployment Engineer
- **Blocker**: Stages 3-4 complete; containers built and Helm chart ready

**Stage 6: Monitoring & Observability** (8-12 hours, ~15 tasks)
- Create Prometheus deployment and scrape config
- Create Grafana deployment and pre-built dashboards
- Create Loki deployment and log scraping config
- Add Prometheus annotations to application pods
- Create Grafana dashboards (request rate, latency, error rate, pod health)
- Create AlertManager rules (error rate >1%, latency p95 >2s, pod restarts)
- Test metrics collection and alerting
- **Owner**: Observability AIOps Agent
- **Blocker**: Stage 3 complete; Helm chart deployed

**Stage 7: OKE Provisioning & Deployment** (10-15 hours, ~20 tasks)
- Provision Oracle OKE cluster (free tier 4 OCPU, 24GB RAM)
- Configure kubectl context
- Deploy Dapr to OKE cluster
- Deploy Strimzi operator and Kafka cluster
- Deploy monitoring stack (Prometheus, Grafana, Loki)
- Deploy application via Helm
- Configure TLS and Ingress
- Document OKE setup procedures
- **Owner**: Cloud Deployment Engineer + Blueprint GitOps Engineer
- **Blocker**: Stages 1, 3-6 complete

**Stage 8: End-to-End Validation & Testing** (6-10 hours, ~15 tasks)
- Verify all 7 Part A user stories work in Minikube deployment
- Verify event-driven flow: task created → Kafka event → audit log + reminder
- Verify Minikube → OKE feature parity
- Load test: 1000 concurrent users
- Chaos test: pod delete → auto-recovery
- Security test: NetworkPolicy enforcement, RBAC validation, secret scanning
- Document test results
- Create <90 second demo video
- **Owner**: Integration Tester
- **Blocker**: All stages complete; application deployed to both Minikube and OKE

### Implementation Dependencies

```
Stage 1 (Dapr + Kafka)
  ↓ (required by)
  ├→ Stage 2 (Backend events)
  ├→ Stage 3 (Helm manifests)
  └→ Stage 7 (OKE deployment)
     ↓
Stage 4 (Docker builds)
  ↓ (required by)
  └→ Stage 5 (CI/CD pipeline)
     ↓
Stage 3 (Helm) + Stage 4 (Docker) + Stage 5 (CI/CD)
  ↓ (required by)
  └→ Stage 6 (Monitoring)
  └→ Stage 7 (OKE deployment)
     ↓
Stage 2 + Stage 6 + Stage 7
  ↓ (required by)
  └→ Stage 8 (E2E testing)
```

---

## Complexity Tracking

No Constitutional violations identified. All Phase 5 design decisions justified and documented in research.md. Multi-service architecture (frontend, backend, optional audit/reminder services) justified by event-driven requirement for multi-consumer pattern.

---

## Quality Gates

### Pre-Implementation Gate 1: Specification Approval ✅ PASS
- Specification: `specs/004-event-driven-cloud/spec.md` → APPROVED and committed
- Quality checklist: `specs/004-event-driven-cloud/checklists/requirements.md` → 13/13 PASS

### Pre-Implementation Gate 2: Constitution Compliance ✅ PASS
- Spec-driven development: spec available for all agents → ✅
- Strict agent boundaries: roles defined for 12+ specialized agents → ✅
- Multi-user isolation: all queries/commands reference user_id → ✅
- Spec approval requirement: all agents will verify → ✅
- No manual coding: all YAML/Docker/Helm agent-generated → ✅

### Pre-Implementation Gate 3: Research Complete
- Phase 0 research findings documented in research.md → PENDING (will complete in Phase 0)
- All unknowns resolved → PENDING (will complete in Phase 0)

### Pre-Implementation Gate 4: Planning Complete ✅ PASS
- Phase 1 design artifacts generated → PENDING (will complete in Phase 1)
- Data model finalized → PENDING (will complete in Phase 1)
- Contracts defined → PENDING (will complete in Phase 1)
- Quickstart documented → PENDING (will complete in Phase 1)

---

## Next Steps

1. **Phase 0 Research**: Execute 8 concurrent research tasks (2-3 hours)
   - Dapr integration strategy
   - Kafka topic design
   - Oracle OKE free tier setup
   - GitHub Actions OKE authentication
   - External-secrets operator
   - Helm chart parameterization
   - Production Kubernetes security
   - Prometheus metrics collection

2. **Phase 1 Design**: Generate design artifacts (4-6 hours, parallel)
   - research.md (research findings)
   - data-model.md (event schemas, Dapr components)
   - contracts/ (Kafka events, Helm values)
   - quickstart.md (local and cloud setup)

3. **Phase 2 Implementation**: Execute 100-125 tasks across 8 stages (40-60 hours, highly parallelizable)
   - Stage 1: Dapr & Kafka Foundation
   - Stage 2: Backend Event Integration
   - Stage 3: Helm Chart & Kubernetes Manifests
   - Stage 4: Docker Multi-Stage Builds
   - Stage 5: CI/CD Pipeline
   - Stage 6: Monitoring & Observability
   - Stage 7: OKE Provisioning & Deployment
   - Stage 8: End-to-End Validation

---

## Agent Coordination

| Agent | Responsible For | Phase | Duration |
|-------|-----------------|-------|----------|
| Dapr Specialist | Dapr sidecars, components, service invocation | 1-2 | 8-12 hrs |
| Dapr Kafka Engineer | Kafka integration, producers, consumers, schemas | 1-2 | 10-15 hrs |
| Event-Driven Architect | Event flows, topic design, multi-consumer pattern | 0-1 | 2-3 hrs |
| Backend Engineer | Event publishing, audit/reminder services | 2 | 10-15 hrs |
| Cloud Deployment Engineer | Docker builds, OKE provisioning, Helm deployment | 2-3 | 20-30 hrs |
| Blueprint GitOps Engineer | Helm charts, values files, RBAC, NetworkPolicy | 2 | 12-18 hrs |
| K8s Production Hardening | Security policies (NetworkPolicy, RBAC, PSA) | 2 | 4-6 hrs |
| Observability AIOps Agent | Prometheus, Grafana, Loki, alerting, AIOps tools | 2-3 | 8-12 hrs |
| CI/CD Engineer | GitHub Actions workflow, image push, deployment | 2-3 | 6-10 hrs |
| Integration Tester | E2E validation, load testing, chaos testing, demo | 3 | 6-10 hrs |
| Documentation | README, deployment.md, quickstart, demo video | 3 | 4-6 hrs |

---

## Success Criteria (from Specification)

✅ Measurable outcomes defined in spec.md (14 success criteria):
- SC-001: Minikube deployment <5 min → pods Ready
- SC-002: All 7 Part A user stories work
- SC-003: Recurring auto-create within 5 seconds
- SC-004: Reminders 98% on-time delivery
- SC-005: 100% audit event capture
- SC-006: OKE deployment <30 min
- SC-007: Zero-downtime rolling updates
- SC-008: CI/CD <10 min build/deploy
- SC-009: Prometheus metrics real-time <30s latency
- SC-010: Kafka lag <5 seconds
- SC-011: Pod recovery <2 min
- SC-012: No secrets in Git/images
- SC-013: 1000 concurrent requests
- SC-014: Event idempotency verified

---

## Estimated Timeline

| Phase | Duration | Start | End | Parallel | Blockers |
|-------|----------|-------|-----|----------|----------|
| Phase 0 (Research) | 2-3 hrs | Day 1 | Day 1 | Yes | None |
| Phase 1 (Design) | 4-6 hrs | Day 1 | Day 2 | Partial | Phase 0 |
| Phase 2 (Implement) | 40-60 hrs | Day 2 | Day 7-8 | Yes | Phase 1 |
| Phase 3 (Test/Deploy) | 6-10 hrs | Day 8 | Day 8 | No | Phase 2 |
| **Total** | **52-79 hrs** | | | | |

With full parallelization (8-12 agents): **6-8 business days**

---

## Risk Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| OKE free tier insufficient resources | Medium | High | Pre-test Kafka+monitoring on 4 OCPU; use single Kafka broker if needed |
| GitHub Actions auth to OKE fails | Low | High | Document OKE kubeconfig + service account setup early; test in Phase 2 start |
| Dapr component configuration mismatch | Medium | Medium | Test Dapr components locally (Minikube) before cloud deployment |
| Event schema incompatibility across services | Low | High | Define schemas in contracts/ early; validate with schema registry if needed |
| Kubernetes resource limits too tight | Medium | Medium | Monitor pod metrics; adjust resource requests/limits in values.yaml |

---

## References & Compliance

- **Constitution**: Follow phase 5 principles (spec-driven, strict agents, multi-user isolation, security enforcement)
- **Specification**: Implement exactly per `/specs/004-event-driven-cloud/spec.md`
- **Technology Stack**: Use Dapr, Kafka, Kubernetes, Prometheus/Grafana/Loki, Oracle OKE free tier as specified
- **Agent Boundaries**: Each agent operates within defined scope only
- **No Manual Coding**: All YAML, Dockerfiles, Helm charts generated by agents

---

**Status**: ✅ Implementation Plan COMPLETE and READY FOR EXECUTION

**Next Command**: `/sp.tasks` to break Phase 2 implementation into 100-125 specific, executable tasks

