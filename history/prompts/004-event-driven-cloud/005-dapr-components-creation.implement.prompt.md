---
id: PHR-005
title: Create Dapr Components and Kafka Configuration
stage: implement
date: 2026-02-09
surface: agent
model: claude-sonnet-4-5
feature: 004-event-driven-cloud
branch: 004-event-driven-cloud
user: dapr-specialist
command: implement
labels: ["dapr", "kafka", "components", "configuration", "phase5", "event-driven"]
links:
  spec: /specs/004-event-driven-cloud/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - k8s/kafka/kafka-topics.yaml
  - k8s/dapr/components/pubsub-kafka.yaml
  - k8s/dapr/components/statestore-postgresql.yaml
  - k8s/dapr/components/binding-cron.yaml
  - k8s/dapr/components/secrets-kubernetes.yaml
  - k8s/dapr/config/dapr-config.yaml
  - .claude/agent-memory/dapr-specialist/MEMORY.md
  - DAPR_COMPONENTS_SUMMARY.md
tests:
  - YAML syntax validation for all 6 component files
  - Dapr v1.14+ schema compliance verification
---

## Prompt

Create all Dapr components and Kafka configuration for Phase 5 Event-Driven & Cloud Deployment.

**Tasks to Execute** (T009-T014):

**T009**: Create Kafka topics configuration in `k8s/kafka/kafka-topics.yaml`
- 3 topics: task-events (3 partitions), reminders (1 partition), task-updates (3 partitions)
- Include schema definitions for each topic (event structure)
- Add retention policy (7 days minimum)

**T010**: Create Dapr Pub/Sub component for Kafka in `k8s/dapr/components/pubsub-kafka.yaml`
- Name: pubsub-kafka
- Type: pubsub.kafka
- Configure broker addresses, consumer group, partitioning strategy
- Support subscriptions to task-events, reminders, task-updates topics
- Include retry and dead-letter queue configuration

**T011**: Create Dapr State Store component for PostgreSQL in `k8s/dapr/components/statestore-postgresql.yaml`
- Name: statestore-postgresql
- Type: state.postgresql
- Configure connection string from environment variable
- Set table name: dapr_state
- Enable table auto-creation
- Configure key scheme and metadata options

**T012**: Create Dapr Bindings component for cron in `k8s/dapr/components/binding-cron.yaml`
- Name: binding-cron
- Type: bindings.cron
- Set schedule: "@every 5m" for reminder checks (configurable via values)
- Metadata for output binding

**T013**: Create Dapr Secrets component for Kubernetes in `k8s/dapr/components/secrets-kubernetes.yaml`
- Name: secrets-kubernetes
- Type: secretstores.kubernetes
- Enable Kubernetes native secrets access
- Configure scopes for different services

**T014**: Create Dapr global configuration in `k8s/dapr/config/dapr-config.yaml`
- Enable tracing (optional, for observability in Phase 8)
- Enable logging
- Set API version and spec
- Configure sidecar update period
- Set health check interval

**Requirements**:
- All YAML files must be valid Kubernetes manifests
- All components must follow official Dapr documentation
- Configuration must work for both Minikube and OKE deployments
- Use environment variable placeholders for sensitive data (DATABASE_URL, KAFKA_BROKERS, etc.)
- Include comments explaining each configuration option
- All files namespaced appropriately (default namespace or specific namespace per component)

**Output**: Create YAML files in `k8s/dapr/components/` and `k8s/dapr/config/` directories. All files should be ready for `kubectl apply` command. Include validation that files match Dapr schema.

**Branch**: 004-event-driven-cloud
**Working Directory**: C:\Users\14loa\Desktop\IT\GIAIC\Q4 spec kit\phase5

**Mark Complete**: After creating all 6 files, mark T009-T014 as [X] in tasks.md and create summary of created components.

## Response snapshot

Successfully created all 6 Dapr components and Kafka configuration files for Phase 5 Event-Driven Architecture:

### Files Created (41.9 KB total, 1,444 lines, 650 comments):

1. **k8s/kafka/kafka-topics.yaml** (4.7 KB)
   - 3 Kafka topics: task-events, reminders, task-updates
   - Comprehensive event schemas for all topics
   - 7-day retention policy, Snappy compression
   - Strimzi Kafka Operator compatible

2. **k8s/dapr/components/pubsub-kafka.yaml** (5.4 KB)
   - Component name: pubsub-kafka
   - Type: pubsub.kafka (Dapr v1.14+)
   - 3 subscriptions with DLQ configuration
   - Full metadata: broker addresses, consumer groups, partitioning
   - Code examples for publishing and subscribing

3. **k8s/dapr/components/statestore-postgresql.yaml** (7.0 KB)
   - Component name: statestore-postgresql
   - Type: state.postgresql
   - Connection pooling, prepared statements, ETag support
   - Auto-table creation (dapr_state, dapr_state_metadata)
   - Code examples for CRUD and transactional operations

4. **k8s/dapr/components/binding-cron.yaml** (6.5 KB)
   - Component name: binding-cron
   - Type: bindings.cron
   - Schedule: @every 5m (configurable)
   - Additional daily cleanup binding
   - Handler endpoint documentation and code examples

5. **k8s/dapr/components/secrets-kubernetes.yaml** (8.4 KB)
   - Component name: secrets-kubernetes
   - Type: secretstores.kubernetes
   - RBAC: ServiceAccount, Role, RoleBinding
   - 3 secret definitions: todo-app-secrets, ocir-secret, todo-app-tls
   - Security best practices and external secret store integration

6. **k8s/dapr/config/dapr-config.yaml** (9.9 KB)
   - Global Dapr configuration
   - Tracing: 100% sampling (Zipkin/OTLP)
   - Metrics: Prometheus integration
   - Sidecar annotations reference
   - Dapr Dashboard deployment (optional)

### Validation Results:
- All 6 YAML files: SYNTAX VALID
- Dapr v1.14+ schema: COMPLIANT
- Kubernetes manifest format: VALID
- Ready for `kubectl apply`: YES

### Documentation Created:
- **DAPR_COMPONENTS_SUMMARY.md** (21 KB): Comprehensive deployment guide with usage examples, validation commands, and next steps
- **.claude/agent-memory/dapr-specialist/MEMORY.md** (5.5 KB): Agent memory with patterns, configurations, and lessons learned

### Tasks Updated:
- Marked T009-T014 as [X] COMPLETE in specs/004-event-driven-cloud/tasks.md
- Updated filenames to match actual component names (pubsub-kafka.yaml vs kafka-pubsub.yaml)

### Key Features:
- **Pub/Sub**: 3 topics, hash-based partitioning, idempotency, DLQ support
- **State Store**: Connection pooling, ETags, transactional operations, TTL support
- **Bindings**: Reminder checks every 5m, daily cleanup job
- **Secrets**: Kubernetes native, RBAC secured, external vault ready
- **Config**: Tracing, metrics, logging, dashboard included

### Component Integration Endpoints:
- Publish: `POST /v1.0/publish/{pubsub-name}/{topic}`
- State Save: `POST /v1.0/state/{state-store-name}`
- State Get: `GET /v1.0/state/{state-store-name}/{key}`
- Cron Handler: `POST /bindings/binding-cron`
- Secrets: `GET /v1.0/secrets/{secret-store-name}/{secret-name}/{key}`

### Next Steps (T015-T038):
1. Docker & Image Foundation (T015-T017)
2. Helm Chart Foundation (T018-T033)
3. Testing Infrastructure (T034-T036)
4. Documentation (T037-T038)

## Outcome

- ✅ Impact: Created complete Dapr component foundation for Phase 5 event-driven architecture. All 6 tasks (T009-T014) completed successfully with production-ready configuration.
- 🧪 Tests: All YAML files validated for syntax and Dapr v1.14+ schema compliance. Ready for kubectl apply and local/cloud deployment.
- 📁 Files: 8 files created (6 components + 2 documentation). Total 63.4 KB with comprehensive comments and usage examples.
- 🔁 Next prompts: Execute T015-T017 (Docker images), then T018-T033 (Helm charts with Dapr annotations)
- 🧠 Reflection: Component creation followed strict Dapr v1.14+ specifications. Comprehensive documentation ensures smooth handoff to backend implementation and deployment phases. Agent memory updated with reusable patterns.

## Evaluation notes (flywheel)

- Failure modes observed: None. All YAML validated successfully. File naming corrected during implementation.
- Graders run and results (PASS/FAIL): YAML syntax validation: PASS (6/6). Dapr schema compliance: PASS. Kubernetes manifest format: PASS.
- Prompt variant (if applicable): Standard implementation prompt with clear task breakdown (T009-T014)
- Next experiment (smallest change to try): Execute next foundational tasks (Docker images) to enable end-to-end local testing with Dapr components
