# Feature Specification: Cloud-Native Deployment (Phase 4 Minikube)

**Feature Branch**: `001-cloud-native-deploy`
**Created**: 2026-02-08
**Status**: Draft
**Input**: Deploy complete Todo application (Phase 2 full-stack + Phase 3 AI chatbot) as cloud-native Kubernetes system on local Minikube with zero manual artifact creation.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - DevOps Engineer Deploys Todo App via Docker Compose Locally (Priority: P1)

A DevOps engineer or developer wants to run the complete Todo application locally (frontend, backend, database) using Docker Compose without needing to understand individual container builds. They start a single command and the entire multi-service application becomes available on localhost.

**Why this priority**: This is the foundational user journey that enables local testing and development before Kubernetes deployment. It validates containerization works correctly and must be fully functional before advancing to Minikube.

**Independent Test**: Can be fully tested by running `docker-compose up` and verifying web UI loads on `http://localhost:3000`, chatbot responds, tasks can be created/listed, and auth works. Delivers immediate value for local dev and CI/CD pipelines.

**Acceptance Scenarios**:

1. **Given** developer has Docker Desktop running, **When** they run `docker-compose up` in project root, **Then** all services start and frontend is accessible within 60 seconds
2. **Given** docker-compose is running, **When** user accesses `http://localhost:3000`, **Then** Login page renders and ChatKit interface is visible
3. **Given** authenticated user is in app, **When** they create a task via chatbot, **Then** task is created and visible in list (persisted to database)
4. **Given** docker-compose is running, **When** developer runs `docker-compose down`, **Then** all containers stop gracefully and volumes can be pruned

---

### User Story 2 - DevOps Engineer Deploys Todo App to Minikube via Helm (Priority: P1)

A DevOps engineer wants to deploy the Todo application to a local Minikube cluster using a production-ready Helm chart. They configure minimal overrides and deploy with `helm install`, then access the app via the Minikube ingress.

**Why this priority**: Core Phase 4 requirement—demonstrates cloud-native Kubernetes deployment in local environment. Validates multi-pod orchestration, service discovery, and zero-downtime operation on Minikube.

**Independent Test**: Can be fully tested by installing Helm chart to Minikube, verifying all pods reach Running state, accessing app via ingress URL, and confirming chatbot/tasks functionality within Kubernetes. Demonstrates horizontal scaling and graceful pod recovery.

**Acceptance Scenarios**:

1. **Given** Minikube cluster is running with ingress enabled, **When** engineer runs `helm install todo-app ./k8s/todo-app`, **Then** all pods (frontend, backend) reach Running state within 90 seconds
2. **Given** Helm deployment is complete, **When** engineer accesses ingress URL (e.g., `http://todo-app.local`), **Then** Todo application loads and all features work (auth, tasks, chatbot)
3. **Given** backend pod is running, **When** pod is deleted manually, **Then** Kubernetes immediately creates replacement pod and no downtime is visible to users
4. **Given** Helm chart is deployed, **When** engineer runs `helm upgrade todo-app ./k8s/todo-app --set replicas=3`, **Then** backend scales to 3 replicas and load is distributed

---

### User Story 3 - DevOps Engineer Uses AI Tools for Kubernetes Operations (Priority: P1)

A DevOps engineer wants to use kubectl-ai and kagent tools to perform cluster diagnostics, scaling operations, and root-cause analysis on failures without writing raw kubectl commands or debugging scripts.

**Why this priority**: Phase 4 explicitly requires kubectl-ai or kagent for at least one meaningful operation. Demonstrates AI-powered Kubernetes operations and must be validated with concrete examples.

**Independent Test**: Can be fully tested by executing kubectl-ai prompt (e.g., "scale deployment todo-backend to 3 replicas") or kagent analysis (e.g., "cluster health analysis") and verifying the action completes successfully. Delivers AI-driven operational value.

**Acceptance Scenarios**:

1. **Given** Minikube cluster is running with kubectl-ai installed, **When** engineer runs kubectl-ai prompt "scale deployment todo-backend to 3 replicas", **Then** backend replicas increase to 3 without manual kubectl command
2. **Given** a pod has crashed or restarted, **When** engineer runs kagent "failure root-cause analysis on todo-backend", **Then** kagent provides analysis of failure cause and recommendations
3. **Given** cluster is under load, **When** engineer runs kubectl-ai "generate pod disruption budget for todo-app", **Then** PDB is created and scales operations are protected

---

### User Story 4 - Security & Secrets Management for Production-Ready Deployment (Priority: P2)

A DevOps engineer wants to ensure sensitive environment variables (BETTER_AUTH_SECRET, COHERE_API_KEY, DATABASE_URL) are never embedded in images or Git, and are properly injected via Kubernetes Secrets at runtime.

**Why this priority**: Security is critical for production readiness. Kubernetes Secrets pattern is standard for cloud-native deployments and must be validated.

**Independent Test**: Can be fully tested by inspecting Docker images (no secrets found), checking Git repository (no .env files with secrets), and verifying that Helm deployment injects secrets via Kubernetes Secret objects. Validates zero-secrets-exposure requirement.

**Acceptance Scenarios**:

1. **Given** Docker image is built, **When** image is inspected with `docker history` and `docker inspect`, **Then** no sensitive environment variables are found in layers
2. **Given** Git repository is cloned, **When** repository is searched for secret patterns, **Then** no COHERE_API_KEY, OPENAI_API_KEY, or DATABASE_URL values are present in tracked files
3. **Given** Helm deployment is complete, **When** pod environment is inspected, **Then** sensitive vars are set from Kubernetes Secrets, not hardcoded

---

### User Story 5 - Demo: Zero-Downtime Scaling & Recovery (Priority: P2)

A DevOps engineer wants to demonstrate graceful zero-downtime scaling and pod recovery to stakeholders, showing the application continues serving requests during scale-up and pod failures.

**Why this priority**: Demonstrates enterprise-grade Kubernetes capabilities (graceful shutdown, zero-downtime). Aligns with Phase 4 success criteria ("zero-downtime scaling demo").

**Independent Test**: Can be fully tested by scaling pods while making continuous requests to the app (no 502/503 errors during scale) and deleting pods while load testing (requests continue without interruption). <90s video demo captures this.

**Acceptance Scenarios**:

1. **Given** backend pod is serving requests, **When** `helm upgrade` scales backend from 1 to 3 replicas while load test runs, **Then** no HTTP errors occur and response times remain stable
2. **Given** backend pods are running, **When** one pod is deleted, **Then** within 5 seconds a new pod is created and traffic is rebalanced
3. **Given** pod is terminating, **When** preStop hook executes and terminationGracePeriodSeconds is 30+, **Then** in-flight requests complete before pod fully terminates

---

### Edge Cases

- What happens when Minikube cluster runs out of memory? (Pod eviction and restart behavior documented)
- How does system handle image pull failures in offline/restricted network? (Local image registry fallback via Minikube)
- What happens if a pod crashes immediately after starting? (backoffLimit and restartPolicy behavior)
- How are database migrations handled during pod restart? (Assumes external Neon DB; in-pod schema-as-code not supported)
- What if Helm values contain typos or invalid configuration? (Validation errors caught during `helm lint` and `helm install --dry-run`)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST containerize the Next.js frontend with multi-stage Dockerfile (builder + nginx runtime), expose port 80, serve standalone output
- **FR-002**: System MUST containerize the FastAPI backend with multi-stage Dockerfile (builder + python:3.11/3.12-slim), expose port 8000, run with uvicorn
- **FR-003**: Docker images MUST include HEALTHCHECK instruction (curl to health endpoint) for container orchestration
- **FR-004**: System MUST include dockerignore file excluding node_modules, __pycache__, .git, .env, and build artifacts
- **FR-005**: System MUST run all containers with non-root user (nginx for frontend, appuser for backend) for security
- **FR-006**: System MUST provide docker-compose.yml that orchestrates frontend, backend, and external database services locally
- **FR-007**: System MUST include Helm chart with Chart.yaml, values.yaml, and templates for frontend/backend deployments, services, ingress, and secrets
- **FR-008**: Helm chart MUST support image tag overrides, replica count configuration, and custom environment values via values.yaml
- **FR-009**: Helm chart templates MUST include Kubernetes Secrets for sensitive environment variables (BETTER_AUTH_SECRET, COHERE_API_KEY, DATABASE_URL)
- **FR-010**: System MUST configure liveness and readiness probes (httpGet /health, initialDelaySeconds 30, periodSeconds 10) for pod health monitoring
- **FR-011**: System MUST configure preStop hook and terminationGracePeriodSeconds ≥ 30 for graceful shutdown
- **FR-012**: Kubernetes manifests MUST include security context (runAsNonRoot, runAsUser 1000, fsGroup 1000, allowPrivilegeEscalation false, capabilities.drop ALL)
- **FR-013**: System MUST enable Minikube ingress addon and configure nginx ingress controller for external access
- **FR-014**: System MUST enable Minikube metrics-server addon for resource usage monitoring (kubectl top pods)
- **FR-015**: System MUST document kubectl-ai and kagent usage patterns with at least 3 example prompts for cluster operations
- **FR-016**: System MUST provide deployment.md documentation including cluster setup, Helm installation, troubleshooting, and recovery procedures

### Key Entities

- **Docker Image (Frontend)**: Multi-stage build artifact serving Next.js standalone output via nginx on port 80; includes health check
- **Docker Image (Backend)**: Multi-stage build artifact running FastAPI/uvicorn on port 8000; includes health check
- **Helm Chart**: Package containing Chart.yaml, values.yaml, and Kubernetes manifest templates for todo-app deployment
- **Kubernetes Deployment (Frontend)**: Manages frontend pod replicas, health probes, resource limits, and service connectivity
- **Kubernetes Deployment (Backend)**: Manages backend pod replicas, health probes, database URL injection, API key injection, and service connectivity
- **Kubernetes Service**: ClusterIP services for frontend and backend internal discovery and ingress routing
- **Kubernetes Ingress**: nginx ingress controller with routing rules to expose app externally via hostname (e.g., todo-app.local)
- **Kubernetes Secret**: Stores BETTER_AUTH_SECRET, COHERE_API_KEY, DATABASE_URL for runtime injection into pod environment
- **PersistentVolume/PersistentVolumeClaim**: Not needed for Phase 4 (database is external Neon PostgreSQL); future enhancement for in-cluster databases

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: docker-compose up successfully starts all services and app is accessible at `http://localhost:3000` within 60 seconds
- **SC-002**: Helm chart deploys to Minikube and all pods reach Running state within 90 seconds
- **SC-003**: Application accessed via Minikube ingress URL responds to HTTP requests with 200 status and renders UI correctly
- **SC-004**: Chatbot receives and processes natural language commands correctly inside Kubernetes environment (proves app functionality, not just infrastructure)
- **SC-005**: kubectl-ai and kagent each successfully complete at least one operation (scale, diagnostics, or analysis) without manual kubectl commands
- **SC-006**: Pod restart (via manual delete) completes in under 10 seconds with no downtime visible to end users (connection resilience verified)
- **SC-007**: Horizontal scaling from 1 to 3 replicas completes with zero HTTP 502/503 errors during transition (graceful rollout verified)
- **SC-008**: Zero secrets found in Docker image layers (docker history inspection) or Git repository (secret scanner)
- **SC-009**: Deployment.md documentation includes step-by-step instructions, all commands tested, and troubleshooting guide with at least 5 common issues
- **SC-010**: <90 second demo video captures docker-compose start → Minikube deployment → working chatbot → horizontal scale → AI ops command

## Assumptions

1. **Phase 3 Application Code is Complete**: No changes to app logic required; only deployment artifacts needed
2. **External Database**: Neon PostgreSQL is external; no in-cluster database (simplifies Phase 4 scope)
3. **Local Minikube Only**: No cloud provider integration; all images built and stored locally
4. **Docker Desktop Available**: Developer machines have Docker Desktop with Minikube integration
5. **kubectl-ai and kagent Installed**: Tools are available and connected to Minikube cluster (installation documented in deployment.md)
6. **Helm 3.14+ Available**: Helm CLI available for installation and upgrade operations
7. **No Manual YAML Creation**: All Kubernetes manifests generated by agents from this spec; no hand-written YAML files
8. **Image Registry**: Local Docker images; no external registry (ECR, Docker Hub, etc.) for Phase 4
9. **Non-root User IDs**: Frontend uses nginx user (UID 82 standard), backend uses appuser (UID 1000)
10. **Health Endpoints Exist**: Backend `/health` endpoint exists and returns 200 OK; frontend health checked via HTTP 200 on port 80

## Constraints & Out of Scope

- **Out of Scope**: Cloud provider integration (AWS, GCP, Azure); external registries; persistent storage for app data (except database connection)
- **Constraint**: All artifacts must be 100% agent/AI-generated; no manual Docker/Helm editing
- **Constraint**: Gordon Beta / Garden Beta optional for optimization; not required for Phase 4
- **Constraint**: Minikube cluster is local development environment; no HA/disaster recovery requirements
- **Constraint**: Security hardening is "best practices for local dev"; production hardening would require additional steps (RBAC, network policies, secrets encryption at rest)

## Dependencies & Integration Points

- **Phase 3 Backend**: Existing FastAPI app with `/api/{user_id}/chat`, task CRUD, auth endpoints; must have health check endpoint
- **Phase 3 Frontend**: Existing Next.js app with ChatKit integration; must build to standalone output
- **Database**: External Neon PostgreSQL; connection string via `DATABASE_URL` environment variable
- **LLM Keys**: COHERE_API_KEY, OPENAI_API_KEY must be injected at runtime via Kubernetes Secrets
- **Auth Secret**: BETTER_AUTH_SECRET must be injected at runtime via Kubernetes Secrets
- **Minikube CLI**: `minikube start/stop/delete/addons` commands; kubectl installed
- **Helm CLI**: `helm install/upgrade/uninstall/lint/template` commands
- **kubectl-ai / kagent**: Optional but required for Phase 4 success criteria; installation documented

## Acceptance Test Plan

| Test Case | Input | Expected Output | Acceptance |
|-----------|-------|-----------------|-----------|
| docker-compose start | `docker-compose up -d` | All services Running, frontend responds on :3000 | ✓ Passes if 200 OK within 60s |
| Helm install | `helm install todo-app ./k8s/todo-app` | All pods Running, ingress accessible | ✓ Passes if pods Running within 90s |
| App functionality | Access app via ingress, create task | Task created and visible in list | ✓ Passes if CRUD works in K8s |
| Chatbot in K8s | Send natural language command to chatbot | Task created/listed via chat | ✓ Passes if chatbot works inside pod |
| kubectl-ai scale | kubectl-ai "scale deployment..." | Deployment replicas changed | ✓ Passes if scale completed |
| Pod recovery | Delete running pod | New pod created, traffic uninterrupted | ✓ Passes if 5s recovery, zero errors |
| Zero downtime scale | helm upgrade with replicas++, load test | No HTTP errors during transition | ✓ Passes if zero 502/503 errors |
| Secrets not exposed | Inspect image, check Git repo | No COHERE_API_KEY, OPENAI_API_KEY in artifacts | ✓ Passes if secret scan clean |
| Health checks | kubectl logs / describe pods | Liveness/readiness probes passing | ✓ Passes if no probe failures |
| Documentation | Read deployment.md | All commands listed, troubleshooting complete | ✓ Passes if guide is executable |

## Validation Plan

This specification will be validated against the following quality criteria:

- **No implementation details**: No mention of specific Dockerfile syntax, Helm template helpers, or kubectl flags in requirements
- **Testable requirements**: Each FR can be verified by running commands or inspecting outputs
- **Measurable success criteria**: SC has specific timing (90s), quantifiable metrics (zero errors, 3 replicas), and observable outcomes
- **Independent user stories**: P1 stories (docker-compose, Helm, AI ops) can be tested and demoed independently
- **Clear acceptance**: Each scenario has specific "Given-When-Then" format for testing

---

**Next Steps**: This specification is ready for `/sp.clarify` (if any ambiguities remain) or `/sp.plan` (to generate architecture and implementation tasks).
