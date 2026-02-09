# Feature Specification: Phase V – Event-Driven & Cloud Deployment

**Feature Branch**: `004-event-driven-cloud`
**Created**: 2026-02-09
**Status**: Draft
**Version**: v1.0

## Overview

Complete Phase V by implementing the **event-driven architecture** and **production-grade cloud deployment** of the existing Todo application. This feature integrates Kafka-based events with Dapr abstractions, deploys locally to Minikube for validation, and then scales to Oracle Kubernetes Engine (OKE) with full CI/CD, monitoring, and observability.

**What's NOT changing**: All 7 Phase 5 Part A user stories (priorities, tags, search, filter, sort, recurring, due dates) remain unchanged—this specification builds on top of that completed work.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Deploy Todo App to Minikube with Dapr Support (Priority: P1)

**Scenario**: DevOps engineers deploy the complete Todo application to a local Minikube cluster, with all Dapr components enabled (Pub/Sub, State, Bindings, Secrets, Service Invocation) and full event-driven architecture operational.

**Why this priority**: Foundation for testing event-driven architecture before cloud deployment. Enables developers to validate all features locally without cloud costs. MVP for production readiness.

**Independent Test**: Deploy to Minikube, verify all 7 user stories work (create/read/update/delete tasks, filter, search, recurring auto-create), and confirm Dapr components are healthy (`dapr status -k`).

**Acceptance Scenarios**:

1. **Given** a Minikube cluster with 4+ CPUs and 8GB+ RAM, **When** running `helm install todo ./helm/todo`, **Then** all pods become Ready within 3 minutes
2. **Given** deployed application, **When** accessing frontend at `http://localhost:3000`, **Then** web UI loads and user can create/complete tasks
3. **Given** running application, **When** executing `dapr status -k`, **Then** Dapr sidecar reports all components healthy (state, pubsub, bindings, secrets)
4. **Given** completed task with recurrence rule, **When** marked complete, **Then** next instance auto-creates via Dapr Pub/Sub event (visible within 5 seconds)
5. **Given** task due date approaching, **When** cron binding triggers at reminder time, **Then** reminder event published and audit logged

---

### User Story 2 - Implement Event-Driven Reminder & Notification System (Priority: P1)

**Scenario**: System publishes reminder events when due dates approach. Notification service consumes these events and stores them for display. All events flow through Kafka via Dapr Pub/Sub.

**Why this priority**: Core event-driven feature; demonstrates Dapr Pub/Sub integration and stateless microservice pattern. Required for Part C cloud deployment validation.

**Independent Test**: Set task due date 1 hour in future, verify reminder event published to `reminders` topic within 5 minutes of due time, and notification stored in database.

**Acceptance Scenarios**:

1. **Given** task with due_date set and reminder_offset configured, **When** Dapr cron binding fires at reminder time, **Then** reminder event published to `reminders` Kafka topic
2. **Given** reminder event in Kafka topic, **When** notification service consumes it, **Then** notification record created in database with status "pending"
3. **Given** notification in database, **When** frontend polls `/api/reminders`, **Then** reminder displayed with task details and due date
4. **Given** multiple reminders queued, **When** consumer processes them, **Then** events processed in order (FIFO) with no duplicates lost
5. **Given** malformed reminder event, **When** consumer receives it, **Then** event logged to dead-letter queue and system continues processing

---

### User Story 3 - Implement Audit Log via Event Stream (Priority: P2)

**Scenario**: Every task CRUD operation (create, update, delete, complete) publishes an event to the audit topic. Audit service consumes these events and records them for compliance and debugging.

**Why this priority**: Compliance requirement; demonstrates multi-consumer pattern (reminder service + audit service both consume from `task-events`). Validates Dapr Pub/Sub can handle multiple independent consumers.

**Independent Test**: Create/update/delete a task, verify audit events appear in audit log with correct user_id, operation type, and timestamp.

**Acceptance Scenarios**:

1. **Given** user creates task via API, **When** task persisted, **Then** `task_created` event published to `task-events` topic with task_id, user_id, timestamp
2. **Given** `task_created` event in Kafka, **When** audit service consumes it, **Then** audit record stored with operation="CREATE", user_id, task_data snapshot
3. **Given** task status updated to completed, **When** update persisted, **Then** `task_completed` event published with old/new status for comparison
4. **Given** task deleted, **When** deletion committed, **Then** `task_deleted` event published with task_id for soft-delete or permanent record
5. **Given** audit records in database, **When** compliance officer queries audit log for user, **Then** all operations for that user listed with timestamps in chronological order

---

### User Story 4 - Deploy Todo App to Oracle OKE Cloud (Priority: P2)

**Scenario**: DevOps engineers provision an Oracle OKE cluster (using free tier), configure kubectl context, and deploy the Todo application using Helm charts. Application is publicly accessible via Ingress with TLS.

**Why this priority**: Production cloud deployment; validates application scales beyond local development. Free tier OKE reduces cost barriers. Demonstrates infrastructure-as-code via Helm.

**Independent Test**: Provision OKE cluster, deploy via Helm, access public URL, and verify all features work (create/complete tasks, filters, search, chatbot).

**Acceptance Scenarios**:

1. **Given** Oracle account with free tier eligibility, **When** provisioning 4 OCPU / 24GB RAM OKE cluster, **Then** cluster ready within 30 minutes
2. **Given** OKE cluster ready, **When** running `helm install todo ./helm/todo -f values-oke.yaml`, **Then** all pods Ready within 5 minutes
3. **Given** deployed application, **When** accessing public Ingress URL, **Then** frontend loads over HTTPS with valid certificate
4. **Given** user interacting with web UI on OKE, **When** creating/completing tasks, **Then** operations persisted to Neon PostgreSQL and reflected in real-time
5. **Given** pod failure on OKE, **When** pod is deleted, **Then** Kubernetes automatically restarts pod and service remains available (self-healing)

---

### User Story 5 - Implement CI/CD Pipeline (GitHub Actions) (Priority: P2)

**Scenario**: GitHub Actions workflow automatically builds Docker images, pushes to registry, and deploys to OKE cluster whenever code is pushed to main branch.

**Why this priority**: Enables continuous deployment; eliminates manual deployment steps. Validates infrastructure reproducibility. Requires integration of all previous features.

**Independent Test**: Push code change to main branch, verify workflow triggers, images build successfully, and new version deployed to OKE within 3 minutes.

**Acceptance Scenarios**:

1. **Given** push to main branch, **When** GitHub Actions workflow triggered, **Then** `build` job starts within 30 seconds
2. **Given** build job running, **When** Docker images built for frontend and backend, **Then** images tagged with commit SHA and pushed to registry within 2 minutes
3. **Given** images in registry, **When** `deploy` job triggered, **Then** Helm chart updated with new image tags and deployed to OKE
4. **Given** deployment in progress, **When** liveness probes on new pods pass, **Then** ingress traffic gradually shifted to new pods (rolling update)
5. **Given** deployment failure (image pull error, pod crash), **When** rollback triggered, **Then** previous stable version restored within 1 minute

---

### User Story 6 - Implement Monitoring & Observability (Priority: P3)

**Scenario**: Prometheus scrapes metrics from application pods, Grafana displays dashboards showing request latency, error rates, Kafka topic lag, and pod health. Logs aggregated via Loki.

**Why this priority**: Production readiness; enables debugging and performance optimization in cloud environment. Required for SLA compliance and incident response.

**Independent Test**: Access Grafana dashboard and verify metrics displayed (request rate, latency p95, error rate). Check Loki for application logs from past hour.

**Acceptance Scenarios**:

1. **Given** application running with Prometheus annotations, **When** Prometheus scrapes metrics, **Then** job targets show pods as "Up" and metrics collected every 15 seconds
2. **Given** metrics collected, **When** accessing Grafana dashboard, **Then** panels display request rate, latency (p50/p95/p99), and error rate
3. **Given** requests flowing through application, **When** checking Kafka consumer lag metric, **Then** lag for all topics under 5 seconds (healthy)
4. **Given** application logs written to stdout, **When** Loki collector scrapes logs, **Then** logs indexed and queryable by pod, namespace, user_id
5. **Given** pod crashes, **When** querying logs in Loki, **Then** error messages and stack traces visible for root cause analysis

---

### Edge Cases

- What happens if Kafka broker becomes unavailable during event publishing? → Event publishing should fail gracefully with retry; Dapr should handle backoff
- How does system handle duplicate event consumption? → Audit service should be idempotent (event_id tracked to prevent double-recording)
- What if OKE node fails? → Pod automatically restarts on healthy node; persistent data in Neon PostgreSQL remains intact
- How does system handle network partition between services? → Dapr service invocation should timeout; requests should fail fast (not hang indefinitely)
- What if reminder event published but notification service is offline? → Event remains in Kafka topic; service resumes consuming when back online (Dapr handles offset tracking)

---

## Requirements *(mandatory)*

### Functional Requirements

#### Event-Driven Architecture (Part A Remaining)

- **FR-001**: System MUST publish `task_created` event to `task-events` Kafka topic when task created (contains task_id, user_id, task_data, timestamp)
- **FR-002**: System MUST publish `task_updated` event to `task-events` topic when task fields modified (contains old and new values for audit trail)
- **FR-003**: System MUST publish `task_deleted` event to `task-events` topic when task deleted (contains task_id, user_id, deletion timestamp)
- **FR-004**: System MUST publish `task_completed` event to `task-events` topic when task status changes to completed (triggers recurring auto-create, sends reminder if configured)
- **FR-005**: System MUST define `reminders` Kafka topic for due-date reminder events published by cron binding
- **FR-006**: System MUST define event schema as JSON with fields: `event_type`, `task_id`, `user_id`, `timestamp`, `task_data` (optional), `event_id` (unique, for idempotency)
- **FR-007**: System MUST use Dapr Pub/Sub component with Kafka for all event publishing/subscribing (no direct Kafka client calls)
- **FR-008**: System MUST use Dapr State component (PostgreSQL backing) for task and notification persistence (no direct database calls from MCP)
- **FR-009**: System MUST use Dapr Bindings component with cron for reminder scheduling (no background job scheduler)
- **FR-010**: System MUST use Dapr Secrets component (Kubernetes secrets backing) for database credentials, API keys, and sensitive config
- **FR-011**: System MUST use Dapr Service Invocation for all inter-service calls (notification service calls task service, etc.)

#### Minikube Deployment (Part B)

- **FR-012**: System MUST be deployable to Minikube (4+ CPUs, 8GB+ RAM) via Helm chart with single command
- **FR-013**: Helm chart MUST include Dapr injection on all deployments (dapr.io/enabled: "true" annotation)
- **FR-014**: Helm chart MUST configure Dapr components: kafka-pubsub, postgresql state, cron bindings, kubernetes-secrets, service-invocation
- **FR-015**: System MUST include Ingress resource for external access to frontend (HTTP on localhost:3000 when port-forwarded)
- **FR-016**: All pods MUST include liveness, readiness, and startup probes with appropriate timeouts and thresholds
- **FR-017**: System MUST pass all Phase 5 Part A feature tests when deployed to Minikube (user stories 1-7 from intermediate/advanced features spec)

#### Oracle OKE Cloud Deployment (Part C)

- **FR-018**: System MUST be deployable to Oracle OKE (free tier) with values-oke.yaml override file
- **FR-019**: OKE deployment MUST use Neon PostgreSQL as external state store (Dapr points to Neon URL)
- **FR-020**: OKE deployment MUST use Redpanda Cloud (free serverless tier) OR self-hosted Strimzi Kafka operator for event streaming
- **FR-021**: Helm chart MUST support environment-specific values (dev/staging/prod) with image registry, replica counts, resource limits overridable
- **FR-022**: All container images MUST use non-root user (UID 1000) and run with read-only root filesystem where possible
- **FR-023**: NetworkPolicy MUST be applied: default deny-all ingress + allow from Ingress controller + allow internal service-to-service communication
- **FR-024**: Ingress MUST use cert-manager for TLS certificate generation (Let's Encrypt staging/production)
- **FR-025**: System MUST support rolling updates with zero downtime (Deployment strategy: rollingUpdate with maxUnavailable=0)

#### CI/CD Pipeline (Part C)

- **FR-026**: GitHub Actions workflow MUST trigger on push to main branch (not on PRs)
- **FR-027**: Workflow MUST build multi-stage Docker images for frontend (Next.js → nginx) and backend (FastAPI → uvicorn)
- **FR-028**: Workflow MUST push images to container registry (GitHub Container Registry / Docker Hub) tagged with commit SHA and "latest"
- **FR-029**: Workflow MUST run automated tests (backend pytest, frontend jest) and fail build if tests fail
- **FR-030**: Workflow MUST deploy to OKE via Helm with new image tags using `helm upgrade --install`
- **FR-031**: Workflow MUST support rollback to previous deployment if health checks fail (automatic or manual trigger)
- **FR-032**: Workflow MUST log all deployment steps and output URLs for accessing deployed application

#### Monitoring & Observability (Part C)

- **FR-033**: All application pods MUST expose Prometheus metrics on `/metrics` endpoint (port 8001)
- **FR-034**: Helm chart MUST include ServiceMonitor or Prometheus scrape config targeting all application metrics endpoints
- **FR-035**: Grafana dashboards MUST display: request rate (req/sec), latency (p50/p95/p99 ms), error rate (%), Kafka topic lag (ms)
- **FR-036**: Grafana dashboards MUST include: pod CPU/memory usage, pod restart count, Dapr sidecar health status
- **FR-037**: All application logs MUST be written to stdout/stderr in JSON format with fields: timestamp, level, message, user_id, trace_id
- **FR-038**: Loki MUST scrape logs from all pods and index by namespace, pod, container, user_id, trace_id
- **FR-039**: Alerting rules MUST trigger if: error rate > 1%, latency p95 > 2s, pod restart rate > 1/hour, Kafka lag > 60s

### Key Entities

- **Event**: Published to Kafka topics; contains event_type, task_id, user_id, timestamp, optional task_data snapshot
- **Kafka Topic**: `task-events` (CRUD events), `reminders` (due-date reminder events), `audit-log` (audit trail)
- **Reminder**: Due-date event triggered by Dapr cron binding; creates notification record for frontend display
- **Audit Log**: Immutable record of every task operation with user_id, operation type, timestamp, data snapshot
- **Deployment**: Kubernetes Deployment for frontend and backend; includes Dapr sidecar injection and health probes
- **Helm Chart**: Parameterized YAML templates for replicable deployments across Minikube/OKE environments

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Minikube deployment succeeds with all pods Ready in under 5 minutes (`kubectl get pods` shows all Running)
- **SC-002**: All 7 Phase 5 Part A user stories work in Minikube deployment (priorities, tags, search, filter, sort, recurring, due dates)
- **SC-003**: Recurring task auto-creation triggered via event and completes within 5 seconds of parent task completion
- **SC-004**: Reminder event published within 5 minutes of due-date reminder time (98% on-time delivery)
- **SC-005**: Audit events captured for 100% of task CRUD operations with no data loss
- **SC-006**: OKE deployment succeeds and application accessible via public Ingress URL within 30 minutes of `helm install`
- **SC-007**: Rolling update deployments complete with zero downtime (user requests never return 5xx errors during deployment)
- **SC-008**: CI/CD pipeline builds, tests, and deploys to OKE in under 10 minutes from code push
- **SC-009**: Prometheus metrics collected for 100% of pods; Grafana dashboards display real-time metrics with <30 second latency
- **SC-010**: Kafka consumer lag stays under 5 seconds for all topics during normal operation (95th percentile)
- **SC-011**: Pod auto-recovery succeeds within 2 minutes of pod deletion (Kubernetes restarts pod and service remains available)
- **SC-012**: All secrets stored in Kubernetes secrets (Dapr Secrets component) or Oracle Vault; no secrets appear in Git or Docker images
- **SC-013**: System handles 1000 concurrent requests without error or performance degradation (load test baseline)
- **SC-014**: Event-driven operations complete idempotently (duplicate event delivery doesn't cause duplicate audit records or notifications)

---

## Assumptions

- **Dapr**: Dapr runtime available on Minikube and OKE clusters (installed via `dapr init -k` or Dapr Helm chart)
- **Kubernetes**: Minikube running with 4+ CPUs and 8GB+ RAM; OKE cluster with 4 OCPUs and 24GB RAM (free tier)
- **PostgreSQL**: Neon managed database used for all persistent state (Phase 5 Part A already uses this; Dapr state component points to Neon)
- **Kafka**: For Minikube, Strimzi Kafka operator in cluster; for OKE, can use self-hosted Strimzi or managed Redpanda Cloud (free tier)
- **Container Registry**: GitHub Container Registry (ghcr.io) used for image storage; alternative is Docker Hub
- **Secrets Management**: Kubernetes secrets for Minikube; Oracle Vault or external-secrets operator for OKE
- **Monitoring Stack**: Prometheus + Grafana for metrics; Loki for logs (or equivalent Oracle cloud-native alternatives)
- **Existing Code**: Phase 2 full-stack, Phase 3 AI chatbot, and Phase 5 Part A features already implemented; this spec builds on top

---

## Dependencies & Constraints

### External Dependencies

- **Neon PostgreSQL**: Managed database for state persistence (Phase 5 Part A already integrated)
- **Dapr Runtime**: Event-driven abstractions and service mesh capabilities
- **Kubernetes**: Minikube for local testing; Oracle OKE for cloud
- **Kafka**: Event streaming backbone (self-hosted or managed)
- **GitHub**: Repository and Actions for CI/CD
- **Container Registry**: Image storage for CI/CD pipeline

### Technical Constraints

- **No Manual kubectl apply**: All Kubernetes resources must be generated via Helm (agent-generated YAML only)
- **No Custom CRDs**: Use standard Kubernetes resources (Deployment, Service, Ingress, ConfigMap, Secret)
- **No Multi-Region**: Single region deployment (Minikube locally, OKE in single region)
- **No Disaster Recovery**: No backup/restore or failover capabilities in scope
- **Stateless Pods**: All state external (Neon DB, Dapr state, Kafka); pods must be interchangeable

---

## Out of Scope

- New Todo features (priorities, tags, search, filter, sort, recurring, due dates) — these are already implemented in Phase 5 Part A
- Custom operators or controllers for Kubernetes
- Multi-region or disaster recovery setup
- Network policies beyond basic ingress allow
- Advanced Dapr features (service mesh, mTLS, fine-grained RBAC)
- Backup and restore procedures (beyond Neon's automated backups)

---

## References & Rules

- Constitution: All features must comply with `.specify/memory/constitution.md`
- Spec-Driven Development: All code generated from this spec by appropriate agents
- Reuse: Phase 2, 3, 4, and 5 Part A code and artifacts leveraged (no reimplementation)
- Oracle OKE: Always-free tier required (4 OCPUs, 24GB RAM)
- Redpanda Cloud: Preferred for Kafka (free serverless tier) if not using self-hosted Strimzi
- All YAML: Agent-generated Kubernetes manifests and Helm templates (no manual editing)
- No Secrets in Git: Environment variables, `.env` files, and secret values never committed

---

## Next Steps

1. **Clarify architectural decisions** (if needed via `/sp.clarify`)
2. **Generate planning artifacts** (via `/sp.plan`) including design decisions, data flow diagrams, and component architecture
3. **Generate implementation tasks** (via `/sp.tasks`) with clear dependencies and parallelization strategy
4. **Execute implementation** (via `/sp.implement`) with specialized agents for backend, cloud deployment, CI/CD, and monitoring

