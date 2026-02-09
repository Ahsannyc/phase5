# Feature Specification: Phase 5 – Advanced Cloud Deployment with Event-Driven Architecture

**Feature Branch**: `002-advanced-cloud-events`
**Created**: 2026-02-08
**Status**: Ready for Planning
**Constitution Reference**: [Phase 5 Constitution](../../.specify/memory/constitution.md)

---

## Overview

Phase 5 extends the Phase 2-4 Todo application with **three major components**:

1. **Part A: Advanced & Intermediate Features** – Recurring tasks, due dates & reminders, priorities, tags/categories, and full-text search/filter/sort
2. **Part B: Event-Driven Architecture** – Kafka-based event publishing, Dapr integration for pub/sub, state management, bindings, and secrets
3. **Part C: Real Cloud Deployment** – Production-grade Kubernetes deployment (AKS/GKE/OKE), CI/CD pipelines, GitOps, monitoring, security hardening, and AIOps at scale

This feature is a **complete evolution** of the Todo platform from a Phase 4 Minikube local deployment to a **production-ready, event-driven, cloud-native application**.

---

## User Scenarios & Testing

### Part A: Advanced Features

#### User Story US-A1: Recurring Task Scheduling (Priority: P1)

A power user wants to create recurring tasks (daily standup, weekly review, monthly planning) without manually creating each instance. Tasks should repeat on schedules (daily, weekly, monthly) or custom cron expressions. When a recurring task is marked complete, the next instance is automatically created.

**Why this priority**: Recurring tasks reduce manual data entry and are essential for project/life management. This is a core productivity feature requested by most users.

**Independent Test**: A user creates a recurring task (daily standup at 9 AM). System automatically creates instances daily. When today's instance is marked complete, tomorrow's instance appears. Task list shows the next upcoming instance.

**Acceptance Scenarios**:

1. **Given** a user has created a recurring task (daily), **When** they mark today's instance complete, **Then** the next instance (tomorrow) appears in their task list
2. **Given** a user creates a task with cron schedule "0 9 * * MON-FRI", **When** the system runs at 9 AM on a weekday, **Then** the task instance is created for that day
3. **Given** a recurring task is deleted, **When** the user views their task list, **Then** future instances are not created (but past completed instances remain in history)
4. **Given** a user modifies a recurring task's title, **When** the next instance is created, **Then** it reflects the updated title

---

#### User Story US-A2: Due Dates & Smart Reminders (Priority: P1)

A user wants to assign due dates to tasks and receive reminders as the deadline approaches. Reminders can be set to notify at specific times (1 day before, 1 hour before, at due time) or via smart notification rules (e.g., "remind me if I haven't started this 1 day before due date").

**Why this priority**: Due dates and reminders are fundamental productivity features that prevent task deadlines from being missed. Essential for deadline-driven work.

**Independent Test**: A user creates a task with a due date (tomorrow) and sets a reminder for "1 day before". System sends a notification at the configured time. User can snooze or dismiss the reminder.

**Acceptance Scenarios**:

1. **Given** a task has a due date and a reminder set for "1 day before", **When** 1 day before the due date arrives, **Then** a notification is delivered to the user
2. **Given** a user receives a reminder notification, **When** they click "snooze", **Then** the reminder is rescheduled for a later time (default 1 hour)
3. **Given** a task's due date is in the past, **When** the user views the task, **Then** it is visually marked as overdue
4. **Given** a user sets a reminder for "1 hour before due time", **When** the system checks reminders, **Then** it correctly identifies tasks due within 1 hour

---

#### User Story US-A3: Task Priorities & Visual Urgency (Priority: P1)

A user wants to prioritize tasks (high, medium, low) to clearly see what needs immediate attention. The task list can be sorted by priority, and high-priority tasks are visually highlighted. Priority helps users focus on what matters most.

**Why this priority**: Prioritization is essential for time management and focus. Reduces cognitive load when task count is high.

**Independent Test**: A user creates tasks with different priorities. Task list can be sorted by priority (high → low). High-priority tasks are visually distinct. User can quickly change a task's priority.

**Acceptance Scenarios**:

1. **Given** a user has tasks with different priorities, **When** they sort by priority, **Then** tasks are ordered high → medium → low
2. **Given** a task is marked as "high priority", **When** the user views the task list, **Then** it is visually highlighted (color, icon, or visual indicator)
3. **Given** a user changes a task's priority, **When** they refresh or the update is synced, **Then** the change is reflected in the task list
4. **Given** a user filters by priority "high", **When** they view the filtered list, **Then** only high-priority tasks are shown

---

#### User Story US-A4: Tags & Categories for Organization (Priority: P2)

A user wants to tag tasks with custom categories (e.g., "work", "personal", "urgent", "learning") to organize and filter tasks. Tags can be created dynamically, applied to multiple tasks, and used for filtering.

**Why this priority**: Tags provide flexible organization beyond a strict hierarchy. Essential for users with diverse task types.

**Independent Test**: A user creates tasks and applies tags (work, personal). They filter by tag "work" to see only work-related tasks. They can create new tags on-the-fly.

**Acceptance Scenarios**:

1. **Given** a user creates a task and applies tags, **When** they save the task, **Then** tags are associated with the task
2. **Given** a user views the task list and clicks a tag filter, **When** they select tag "work", **Then** only tasks with the "work" tag are shown
3. **Given** a task has multiple tags (work, urgent), **When** the user filters by either tag, **Then** the task appears in both filtered views
4. **Given** a user deletes a tag, **When** they confirm deletion, **Then** the tag is removed from all tasks

---

#### User Story US-A5: Advanced Search, Filter & Sort (Priority: P1)

A user wants powerful search and filtering to find tasks quickly: full-text search on title/description, filter by status (incomplete/complete), priority, due date (today/this week/overdue), tags, and sort by multiple criteria (due date, priority, created date).

**Why this priority**: Search and filtering are critical for usability when task count grows. Essential for power users and professionals.

**Independent Test**: A user searches for "project X", filters by "incomplete + high priority + work tag", and sorts by "due date ascending". Results show matching tasks in the correct order.

**Acceptance Scenarios**:

1. **Given** a user searches for "project X", **When** the search is executed, **Then** tasks with "project X" in title or description are returned
2. **Given** a user applies multiple filters (status=incomplete, priority=high, tag=work), **When** they view results, **Then** only tasks matching ALL criteria are shown
3. **Given** a user sorts by "due date", **When** they view the task list, **Then** tasks are ordered from earliest due date to latest
4. **Given** a user combines search + filter + sort, **When** they view results, **Then** the combination is applied correctly (search → filter → sort)

---

### Part B: Event-Driven Architecture

#### User Story US-B1: Event Publishing for Task Operations (Priority: P1)

The system publishes events to a Kafka topic whenever a task is created, updated, completed, or deleted. Events include metadata (user_id, task_id, timestamp, action, task snapshot). These events enable downstream systems (reminders, notifications, analytics, webhooks) to react in real-time without polling.

**Why this priority**: Event-driven architecture enables scalability, real-time integrations, and decoupling of services. Essential for production systems.

**Independent Test**: A user creates a task via the UI. A Kafka topic receives a task-created event with the correct data. A consumer service reads the event and performs downstream actions (e.g., schedule reminder).

**Acceptance Scenarios**:

1. **Given** a user creates a task, **When** the task is saved, **Then** a "task-created" event is published to Kafka with user_id, task_id, title, description, and timestamp
2. **Given** a user updates a task (title, priority, due date), **When** the update is committed, **Then** a "task-updated" event is published with the old and new values
3. **Given** a user completes a task, **When** the status changes to complete, **Then** a "task-completed" event is published with the completion timestamp
4. **Given** a user deletes a task, **When** the deletion is confirmed, **Then** a "task-deleted" event is published with the deletion timestamp

---

#### User Story US-B2: Dapr Integration for Event Pub/Sub & State Management (Priority: P1)

The backend uses Dapr (Distributed Application Runtime) sidecars to abstract event publishing, state management, and service-to-service communication. All task CRUD events flow through Dapr pub/sub (Kafka), and task reminders/scheduling state is persisted via Dapr state management (PostgreSQL). Services communicate via Dapr service invocation instead of direct HTTP calls.

**Why this priority**: Dapr provides a vendor-neutral abstraction layer, enabling portability across cloud providers and reducing code complexity. Critical for production deployment.

**Independent Test**: The backend publishes a task event through Dapr pub/sub API. Dapr routes the event to Kafka. A consumer service receives the event via Dapr pub/sub. State operations (save reminder state) succeed via Dapr state API.

**Acceptance Scenarios**:

1. **Given** the backend is configured with a Dapr sidecar, **When** an event is published via Dapr pub/sub API, **Then** it reaches the Kafka topic without hardcoding Kafka client code
2. **Given** a service needs to save state (e.g., last reminder sent time), **When** it calls Dapr state API, **Then** the state is persisted in PostgreSQL via Dapr
3. **Given** a service invokes another service (backend calls reminder service), **When** the call uses Dapr service invocation, **Then** it succeeds without needing the target service's IP/URL
4. **Given** Dapr is misconfigured or unavailable, **When** the app starts, **Then** Dapr health checks fail and the pod does not become ready (fails gracefully)

---

#### User Story US-B3: Reminder & Notification Service via Dapr Bindings (Priority: P2)

A separate reminder service (or FastAPI endpoint) consumes task-created and task-updated events, schedules reminders using Dapr bindings (e.g., cron trigger), and sends notifications when reminder time arrives. Reminders state is stored via Dapr state management.

**Why this priority**: Decoupled reminder service demonstrates event-driven architecture and enables scaling of notification logic independently.

**Independent Test**: A user creates a task with a due date. A reminder event is published. The reminder service reads the event, schedules a reminder via Dapr cron binding, and stores state. At reminder time, a notification is triggered.

**Acceptance Scenarios**:

1. **Given** a task is created with a due date and reminder setting, **When** the task-created event is published, **Then** the reminder service reads the event
2. **Given** the reminder service receives a task event, **When** it calculates the reminder time, **Then** it creates a Dapr binding (cron) to trigger at that time
3. **Given** the reminder time arrives, **When** the Dapr binding triggers, **Then** a notification is sent to the user (email, in-app, or webhook)
4. **Given** the user snoozes a reminder, **When** the snooze is saved, **Then** the reminder service updates its state and reschedules the next reminder

---

### Part C: Real Cloud Deployment

#### User Story US-C1: Production Kubernetes Deployment (Priority: P1)

The complete Todo application (frontend, backend, Kafka, Dapr) is deployed to a real cloud Kubernetes cluster (AKS, GKE, or OKE) using Helm charts. The deployment is production-ready with multiple replicas, resource limits, health checks, and auto-scaling.

**Why this priority**: Real cloud deployment is the primary goal of Phase 5. Demonstrates scalability, reliability, and production readiness.

**Independent Test**: A Helm chart is created and deployed to AKS/GKE/OKE. All pods reach Running state. The app is accessible via a public URL. Users can interact with the app (create tasks, chat, see reminders).

**Acceptance Scenarios**:

1. **Given** a Helm chart is prepared, **When** `helm install todo-app ./helm/todo-app` is executed on a real cloud cluster, **Then** all pods (frontend, backend, Kafka broker, reminder service) reach Running state within 5 minutes
2. **Given** the app is deployed, **When** users access the public URL, **Then** the frontend loads and all features are accessible
3. **Given** the backend pod crashes, **When** Kubernetes detects the failure, **Then** a new pod is created and traffic is rebalanced (no user-visible downtime)
4. **Given** traffic increases, **When** the Horizontal Pod Autoscaler threshold is exceeded, **Then** additional replicas are created to handle load

---

#### User Story US-C2: CI/CD Pipeline via GitHub Actions (Priority: P1)

A GitHub Actions workflow automates the build, test, and deployment process: on every push to main, the workflow builds Docker images, runs tests, pushes images to a container registry (ACR, GCR, OCIR), and triggers a Helm deployment to the cloud cluster via GitOps.

**Why this priority**: Automated CI/CD enables fast iteration and reduces manual deployment errors. Essential for production operations.

**Independent Test**: A developer pushes code to main. GitHub Actions automatically builds the app, runs tests, pushes images, and deploys to the cloud cluster. Within 5 minutes, the new version is live.

**Acceptance Scenarios**:

1. **Given** code is pushed to the main branch, **When** the GitHub Actions workflow is triggered, **Then** Docker images are built for frontend and backend
2. **Given** tests are run in the CI pipeline, **When** all tests pass, **Then** images are pushed to the container registry
3. **Given** images are pushed, **When** the GitOps sync is triggered, **Then** the cloud cluster pulls new images and updates deployments
4. **Given** a deployment fails, **When** the workflow detects the failure, **Then** a notification is sent and the deployment can be rolled back

---

#### User Story US-C3: Observability & Monitoring at Scale (Priority: P2)

The cloud deployment includes comprehensive observability: Prometheus collects metrics (request latency, error rate, pod CPU/memory), Grafana visualizes dashboards, and Loki aggregates logs. Alerts are configured for critical metrics (error rate > 5%, pod restart loops, high latency).

**Why this priority**: Observability is essential for understanding production behavior, debugging issues, and maintaining SLAs.

**Independent Test**: A user performs actions in the Todo app. Prometheus metrics appear in real-time. A Grafana dashboard shows request latency, error rate, and pod health. Logs are searchable in Loki.

**Acceptance Scenarios**:

1. **Given** the app is running, **When** users make requests, **Then** Prometheus scrapes metrics (HTTP requests, latency, errors) every 30 seconds
2. **Given** a Grafana dashboard is configured, **When** it displays metrics, **Then** it shows real-time request volume, latency p95/p99, error rate
3. **Given** an error occurs, **When** the app logs the error, **Then** logs are shipped to Loki and searchable by timestamp, pod, error message
4. **Given** error rate exceeds 5%, **When** the alert rule evaluates, **Then** a notification is sent to the ops team

---

#### User Story US-C4: Security Hardening & Zero-Trust (Priority: P1)

The cloud deployment enforces production security: NetworkPolicies restrict pod-to-pod communication, RBAC ensures least privilege, Pod Security Admission prevents privilege escalation, non-root containers, read-only file systems where possible, and secrets are managed via external-secrets operator.

**Why this priority**: Security is non-negotiable for production systems. Protects user data and prevents unauthorized access.

**Independent Test**: A network policy denies all ingress traffic by default. Specific pods are allowed to communicate only with their required services. An attacker cannot access secrets directly from pods.

**Acceptance Scenarios**:

1. **Given** a NetworkPolicy denies all ingress traffic, **When** a pod tries to connect to an unauthorized service, **Then** the connection is blocked
2. **Given** the backend pod runs as non-root (appuser UID 1000), **When** someone tries to execute privileged commands, **Then** they are denied (permission error)
3. **Given** secrets are managed via external-secrets operator, **When** a pod starts, **Then** secrets are injected from the external secret store (not hardcoded in the image)
4. **Given** RBAC roles are configured, **When** a service account tries to access resources outside its permissions, **Then** the access is denied (403 Forbidden)

---

#### User Story US-C5: High Availability & Resilience Demo (Priority: P2)

The deployment demonstrates resilience: horizontal scaling (scale from 2 to 5 replicas under load without downtime), pod recovery (delete a pod → replacement created within 30 seconds), graceful shutdown (preStop hooks allow in-flight requests to complete), and chaotic engineering (intentionally cause failures and demonstrate recovery).

**Why this priority**: High availability is essential for production systems. Demonstrates confidence in the deployment to users and stakeholders.

**Independent Test**: Load test starts generating traffic. Replicas are scaled up while load continues. No HTTP errors occur. A pod is manually deleted. A replacement appears immediately. All traffic is handled smoothly.

**Acceptance Scenarios**:

1. **Given** a continuous load test is running, **When** replicas are scaled from 2 to 5, **Then** no requests fail (HTTP 200 responses continue)
2. **Given** a pod is forcefully deleted, **When** Kubernetes detects the deletion, **Then** a replacement pod is created within 30 seconds
3. **Given** a pod is gracefully shut down, **When** the preStop hook executes, **Then** in-flight requests are allowed to complete before the pod terminates
4. **Given** multiple services (frontend, backend, Kafka, reminder service) are running, **When** one service becomes unavailable, **Then** the system degrades gracefully (partial functionality) or fails over without cascading failures

---

#### User Story US-C6: GitOps & Infrastructure-as-Code (Priority: P2)

All infrastructure (Helm charts, Kubernetes manifests, Dapr components, Prometheus rules, Grafana dashboards) is version-controlled in Git. A GitOps tool (ArgoCD) watches the Git repository and automatically syncs changes to the live cluster. Infrastructure changes follow Git commit → review → merge → auto-deploy workflow.

**Why this priority**: GitOps enables repeatable, auditable infrastructure management. Reduces manual errors and enables disaster recovery.

**Independent Test**: A developer updates the Helm values (e.g., increase replicas) and pushes to Git. ArgoCD detects the change and automatically updates the cluster. No manual kubectl apply needed.

**Acceptance Scenarios**:

1. **Given** infrastructure changes are committed to Git, **When** ArgoCD syncs, **Then** the live cluster matches the Git state
2. **Given** a disaster scenario (cluster corruption), **When** a new cluster is provisioned, **Then** ArgoCD redeploys the exact infrastructure from Git
3. **Given** a developer proposes a change (e.g., new Prometheus alert), **When** it's merged to main, **Then** ArgoCD auto-deploys it to the live cluster
4. **Given** ArgoCD detects a drift (manual change made outside Git), **When** sync runs, **Then** the manual change is reverted to match Git

---

#### User Story US-C7: AIOps at Scale (Priority: P2)

Operations teams use kubectl-ai and kagent to manage the production cluster without manual kubectl commands: scale workloads via natural language, diagnose pod failures with root-cause analysis, optimize resource usage, and maintain cluster health. AIOps tools provide intelligent recommendations and reduce toil.

**Why this priority**: AIOps demonstrates automation and reduces operational burden. Essential for sustainable operations at scale.

**Independent Test**: An ops engineer says "scale backend to handle 10k concurrent users". kubectl-ai suggests resource adjustments and scaling strategies. kagent analyzes cluster health and suggests optimizations.

**Acceptance Scenarios**:

1. **Given** kubectl-ai is configured, **When** an operator asks "scale backend deployment to 10 replicas", **Then** kubectl-ai generates the scaling command and applies it
2. **Given** a pod crashes, **When** kagent analyzes recent logs and events, **Then** it identifies the root cause (out of memory, failed health check, etc.)
3. **Given** cluster metrics are available, **When** kagent is asked "optimize resource usage", **Then** it suggests CPU/memory adjustments based on actual usage patterns
4. **Given** multiple services are running, **When** kagent analyzes cluster health, **Then** it reports on node status, pod health, and potential issues

---

### Edge Cases

- **Recurring task edge case**: What happens if a recurring task is created with a frequency (daily) but the user is in a different timezone? → System stores due dates in UTC; displays in user's local timezone
- **Reminder edge case**: User has 10 reminders scheduled for the same task. → Only one reminder is sent per scheduled time; duplicates are deduplicated
- **Event publishing edge case**: Kafka topic is temporarily unavailable. → Events are queued in memory or persisted to a dead-letter queue; delivery is retried with exponential backoff
- **Cloud deployment edge case**: Container registry is unreachable during deployment. → Pod creation fails; Kubernetes retries with exponential backoff; eventually succeeds when registry is reachable
- **Security edge case**: User attempts to access another user's task via API. → Request is denied (403 Forbidden) after JWT validation confirms user_id mismatch
- **Dapr state edge case**: PostgreSQL connection is lost. → Dapr health check fails; pod is marked as not ready; traffic is not routed to the pod

---

## Requirements

### Functional Requirements

#### Part A: Advanced Features

- **FR-A1**: System MUST allow users to create recurring tasks with schedule rules (daily, weekly, monthly) or custom cron expressions
- **FR-A2**: System MUST automatically create the next instance of a recurring task when the current instance is marked complete
- **FR-A3**: System MUST allow users to assign due dates to tasks and set multiple reminders (1 day before, 1 hour before, at due time)
- **FR-A4**: System MUST send notifications (in-app, email, webhook) when a reminder time arrives
- **FR-A5**: System MUST allow users to snooze reminders; when snoozed, the reminder is rescheduled for a later time (default 1 hour)
- **FR-A6**: System MUST allow users to assign priorities (high, medium, low) to tasks
- **FR-A7**: System MUST visually highlight high-priority tasks in the UI with color, icons, or other indicators
- **FR-A8**: System MUST allow users to create custom tags and apply multiple tags to tasks
- **FR-A9**: System MUST support filtering tasks by tag; filtering by multiple tags shows tasks matching ANY tag (OR logic)
- **FR-A10**: System MUST support full-text search on task title and description
- **FR-A11**: System MUST support filtering by status (incomplete, complete), priority, due date ranges (today, this week, overdue), and tags
- **FR-A12**: System MUST support sorting by multiple criteria (due date ascending/descending, priority, created date, completion date)
- **FR-A13**: System MUST persist all advanced features in the database with proper schema and migrations
- **FR-A14**: Recurring task scheduling MUST work with different user timezones (store in UTC, display in user's timezone)
- **FR-A15**: System MUST handle edge cases (delete recurring task, modify recurring task title, timezone changes)

#### Part B: Event-Driven Architecture

- **FR-B1**: System MUST publish events to a Kafka topic for every task CRUD operation (create, update, complete, delete)
- **FR-B2**: Events MUST include metadata: user_id, task_id, timestamp, action type, task snapshot (title, description, priority, due date, tags)
- **FR-B3**: System MUST use Dapr sidecar for pub/sub; all Kafka interactions go through Dapr pub/sub API (not direct Kafka client)
- **FR-B4**: System MUST use Dapr state management for storing reminder state and scheduling data; backed by PostgreSQL
- **FR-B5**: System MUST implement a reminder service that consumes task events, schedules reminders via Dapr bindings (cron), and sends notifications
- **FR-B6**: System MUST support Dapr service invocation for inter-service communication (e.g., backend calls reminder service)
- **FR-B7**: System MUST handle event delivery guarantees: at-least-once delivery (events may be duplicate; consumers must be idempotent)
- **FR-B8**: System MUST implement proper error handling and dead-letter queues for failed event processing
- **FR-B9**: Dapr MUST be deployed as a sidecar to every service pod in Kubernetes
- **FR-B10**: Event schema MUST be versioned and documented; schema changes maintain backward compatibility

#### Part C: Real Cloud Deployment

- **FR-C1**: System MUST be deployable to real Kubernetes clusters (AKS on Azure, GKE on Google Cloud, OKE on Oracle Cloud)
- **FR-C2**: System MUST provide parameterized Helm charts supporting multiple environments (dev, staging, production) via values overrides
- **FR-C3**: System MUST support CI/CD pipeline via GitHub Actions: build → test → push images → deploy via Helm
- **FR-C4**: System MUST implement Prometheus metrics collection; all services export metrics on /metrics endpoint
- **FR-C5**: System MUST implement Loki log aggregation; all services ship logs to Loki
- **FR-C6**: System MUST provide Grafana dashboards showing key metrics: request latency, error rate, pod CPU/memory, Kafka lag
- **FR-C7**: System MUST implement alerting rules (Prometheus AlertManager): error rate > 5%, pod restart loops, high latency
- **FR-C8**: System MUST enforce NetworkPolicies: deny-all ingress by default; specific pods allowed to communicate with required services only
- **FR-C9**: System MUST implement RBAC with least-privilege service accounts; each service has minimal required permissions
- **FR-C10**: System MUST run all containers as non-root users; root access is denied
- **FR-C11**: System MUST manage secrets via external-secrets operator or cloud secret manager (Azure Key Vault, GCP Secret Manager, OCI Vault)
- **FR-C12**: System MUST implement Horizontal Pod Autoscaling; scale replicas based on CPU or custom metrics (1-10 replicas)
- **FR-C13**: System MUST implement Pod Disruption Budgets (PDB); ensures minimum replicas available during voluntary disruptions
- **FR-C14**: System MUST implement liveness, readiness, and startup probes; pods are health-checked every 30 seconds
- **FR-C15**: System MUST implement preStop hooks; allow in-flight requests to complete before pod termination (30-second grace period)
- **FR-C16**: All Kubernetes manifests MUST be valid, lint-able, and documented
- **FR-C17**: GitOps tool (ArgoCD) MUST manage all deployments; Git is the source of truth for infrastructure
- **FR-C18**: kubectl-ai and kagent MUST be integrated for AIOps operations; documented example commands for scaling, diagnostics, optimization

### Key Entities

#### Advanced Features Entities

- **RecurringTaskSchedule**: Represents the schedule for a recurring task
  - `id`: UUID
  - `task_id`: Foreign key to Task
  - `frequency`: Enum (daily, weekly, monthly, custom)
  - `cron_expression`: String (if custom frequency)
  - `timezone`: String (e.g., "America/New_York", "UTC")
  - `next_instance_due_date`: DateTime
  - `is_active`: Boolean (false when task is deleted or scheduling stopped)

- **TaskReminder**: Represents a reminder setting for a task
  - `id`: UUID
  - `task_id`: Foreign key to Task
  - `reminder_time`: DateTime (absolute time, not relative)
  - `reminder_type`: Enum (email, in-app, webhook)
  - `is_snoozed`: Boolean
  - `snooze_until`: DateTime (if snoozed)
  - `notification_sent`: Boolean

- **Tag**: Represents a user-defined tag/category
  - `id`: UUID
  - `user_id`: Foreign key to User
  - `name`: String (e.g., "work", "personal", "urgent")
  - `color`: String (hex color for UI, e.g., "#FF5733")
  - `created_at`: DateTime

- **TaskTag**: Junction table for many-to-many relationship between Task and Tag
  - `task_id`: Foreign key to Task
  - `tag_id`: Foreign key to Tag

#### Event-Driven Architecture Entities

- **KafkaTopic**: (Configuration, not a database table)
  - `topic_name`: String (e.g., "todo-events")
  - `partitions`: Integer (for parallel processing)
  - `retention_ms`: Integer (how long to keep events)
  - `schema`: JSON Schema for events

- **KafkaEvent**: (Log/audit table, optional)
  - `id`: UUID
  - `topic`: String
  - `event_type`: String (task-created, task-updated, task-completed, task-deleted)
  - `payload`: JSON (the full event)
  - `created_at`: DateTime
  - `processed_at`: DateTime

- **ReminderState**: (Stored via Dapr state management, not a database table)
  - `reminder_id`: String (key)
  - `task_id`: UUID
  - `next_reminder_time`: DateTime
  - `snooze_count`: Integer
  - `notification_sent`: Boolean

#### Real Cloud Deployment Entities

- **DeploymentConfig**: (Infrastructure-as-Code, stored in Helm values.yaml)
  - Environment: dev, staging, production
  - Replicas: 1-10
  - Resource limits: CPU (100m-2000m), Memory (256Mi-4Gi)
  - Image registry: ACR, GCR, OCIR
  - Kafka bootstrap servers
  - Database URL
  - External secret store

---

## Success Criteria

### Measurable Outcomes

#### Part A: Advanced Features
- **SC-A1**: Users can create a recurring task and see it repeat correctly (next instance appears within 1 minute of completion)
- **SC-A2**: Reminders are sent on time (within ±5 minutes of scheduled reminder time)
- **SC-A3**: 95% of reminder notifications are delivered successfully; failed notifications are retried
- **SC-A4**: High-priority tasks are visually distinct and users can sort by priority
- **SC-A5**: Full-text search returns relevant results within 1 second (p95 latency)
- **SC-A6**: Users can apply filters (status, priority, tag, due date) and combinations work correctly
- **SC-A7**: All advanced features work correctly across different user timezones
- **SC-A8**: Task list UI handles 100+ tasks without noticeable performance degradation (render time < 2 seconds)

#### Part B: Event-Driven Architecture
- **SC-B1**: Events are published to Kafka within 100ms of task operation (p95 latency)
- **SC-B2**: At-least-once delivery guarantee: 99.9% of events are processed by consumers (no lost events)
- **SC-B3**: Event consumers process events within 1 second of publication (p95 latency)
- **SC-B4**: Reminder service correctly schedules reminders and sends notifications on time
- **SC-B5**: Dapr sidecars maintain < 5% CPU and < 100Mi memory overhead per pod
- **SC-B6**: Dead-letter queue catches failed events; ops team can investigate and replay failed events
- **SC-B7**: Zero data loss: if Kafka topic becomes unavailable, events are queued and retried when Kafka is back

#### Part C: Real Cloud Deployment
- **SC-C1**: App deploys to cloud cluster (AKS/GKE/OKE) in < 5 minutes using Helm
- **SC-C2**: All pods reach Running state within 2 minutes of deployment; health checks pass
- **SC-C3**: Frontend is accessible via public URL; all features work (create tasks, chat, reminders)
- **SC-C4**: Horizontal scaling: replicas scale from 2 to 10 under load; no downtime (0 HTTP errors during scaling)
- **SC-C5**: Pod recovery: deleted pod is replaced within 30 seconds; no user-visible service interruption
- **SC-C6**: Graceful shutdown: pod terminates cleanly within 30 seconds; in-flight requests are allowed to complete
- **SC-C7**: Observability: Prometheus metrics are collected; Grafana dashboards show real-time metrics
- **SC-C8**: Alerting: alerts are triggered correctly (error rate > 5%, pod restarts, high latency)
- **SC-C9**: Security: NetworkPolicies block unauthorized traffic; RBAC prevents privilege escalation; secrets are not exposed
- **SC-C10**: GitOps: Git changes are automatically synced to live cluster within 30 seconds
- **SC-C11**: CI/CD: code push to main triggers automated build → test → deploy; live within 5 minutes
- **SC-C12**: AIOps: kubectl-ai and kagent commands successfully manage cluster (scale, diagnose, optimize)
- **SC-C13**: Disaster recovery: cluster can be recreated from Git; all infrastructure and data are restored
- **SC-C14**: Cost efficiency: Horizontal scaling and resource optimization reduce per-user cost vs. over-provisioned setup

---

## Constraints & Assumptions

### Assumptions

1. Phase 4 deployment (Minikube + Helm) is complete and working; Phase 5 builds on it
2. Neon PostgreSQL is available as external database; no RDS provisioning in Phase 5
3. Kafka is deployed to the cluster (via Strimzi or managed service like Redpanda)
4. Dapr is installed and configured in the Kubernetes cluster
5. External secret manager (Azure Key Vault, GCP Secret Manager, OCI Vault) is available
6. GitHub Actions is configured; ECR/GCR/OCIR registries are available
7. ArgoCD or Flux is installed for GitOps
8. Prometheus and Loki are available for monitoring (self-hosted or cloud-managed)
9. Users understand the event-driven architecture; events are treated as best-effort (at-least-once delivery)
10. Task event frequency is manageable (< 1000 events/second per user)

### Constraints

1. **Scope**: Phase 5 does NOT include:
   - Advanced AI features beyond Phase 3 chatbot (no ML models, no custom training)
   - Custom Dapr components (only standard Kafka, PostgreSQL, cron, external-secrets)
   - Multi-cluster deployment or disaster recovery with active-active replication
   - Custom Kubernetes operators or CRDs
   - Cost optimization via spot instances or reserved capacity (left to user)

2. **Technology**: Phase 5 MUST use:
   - Kafka for events (Strimzi or managed)
   - Dapr for pub/sub, state, bindings
   - Real Kubernetes (AKS/GKE/OKE, not Minikube)
   - Helm 3+ for deployments
   - GitHub Actions for CI/CD
   - ArgoCD or Flux for GitOps
   - No proprietary lock-ins where possible

3. **Security**: All secrets MUST be managed via external secret store or cloud KMS; NO hardcoded secrets in images/manifests

4. **Multi-user**: User data isolation via user_id is non-negotiable; one user cannot see another's tasks/events

---

## Acceptance Test Plan

| Test ID | Scenario | Steps | Expected Result |
|---------|----------|-------|-----------------|
| AT-A1 | Create recurring task | User creates daily standup task; mark today's instance complete | Tomorrow's instance appears in task list |
| AT-A2 | Set reminder | User creates task with due date tomorrow; set reminder for 1 day before | Notification sent at correct time |
| AT-A3 | Priority filtering | User creates tasks with different priorities; filter by high priority | Only high-priority tasks shown |
| AT-A4 | Tag filtering | User applies tags to tasks; filter by "work" tag | Only tasks with "work" tag shown |
| AT-A5 | Search & filter | User searches "project X"; filter by incomplete + high priority | Correct tasks returned |
| AT-B1 | Event publishing | User creates task; check Kafka topic | task-created event appears in topic |
| AT-B2 | Dapr pub/sub | Service publishes event via Dapr; consumer receives it | Event delivered correctly |
| AT-B3 | Reminder service | Task created; reminder service reads event and schedules reminder | Reminder sent at correct time |
| AT-C1 | Helm deployment | Run `helm install` on cloud cluster | All pods Running; app accessible |
| AT-C2 | Horizontal scaling | Generate load; replicas scale up | No HTTP errors during scaling |
| AT-C3 | Pod recovery | Delete a pod; watch for replacement | New pod created within 30s |
| AT-C4 | Monitoring | Generate traffic; check Prometheus/Grafana | Metrics visible in dashboard |
| AT-C5 | NetworkPolicy | Try to access backend from unauthorized pod | Connection blocked |
| AT-C6 | GitOps sync | Update Helm values in Git; push | ArgoCD syncs changes to cluster |
| AT-C7 | CI/CD pipeline | Push code to main | Build → test → deploy within 5 minutes |
| AT-C8 | AIOps command | Ask kubectl-ai to scale backend | Replicas scaled correctly |

---

## Next Steps

1. **Clarifications** (if needed): Use `/sp.clarify` if requirements need refinement
2. **Architecture Planning**: Use `/sp.plan` to design implementation approach
3. **Task Breakdown**: Use `/sp.tasks` to create actionable implementation tasks
4. **Implementation**: Use `/sp.implement` to execute tasks
5. **Testing & Validation**: Use integration tests to verify all three parts work together

---

**Status**: Ready for planning phase
**Reviewed**: Phase 5 Constitution ✅
**Next Command**: `/sp.plan`
