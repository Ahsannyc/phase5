# Dapr Specialist Memory - Phase 5 Event-Driven Architecture

## Project Context
- **Branch**: 004-event-driven-cloud
- **Namespace**: default (Kubernetes)
- **Dapr Version**: v1.14+
- **Component Directory**: `k8s/dapr/components/`
- **Config Directory**: `k8s/dapr/config/`
- **Kafka Directory**: `k8s/kafka/`

## Component Inventory

### Created Components (T009-T014 Complete)
1. **pubsub-kafka.yaml** - Pub/Sub component for Kafka messaging
2. **statestore-postgresql.yaml** - State Store for PostgreSQL persistence
3. **binding-cron.yaml** - Cron binding for scheduled reminders
4. **secrets-kubernetes.yaml** - Kubernetes native secrets integration
5. **dapr-config.yaml** - Global Dapr configuration
6. **kafka-topics.yaml** - Kafka topic definitions with schemas

### Component Naming Convention
- Format: `<component-type>-<technology>.yaml`
- Examples: `pubsub-kafka.yaml`, `statestore-postgresql.yaml`
- Follows Dapr v1.14+ component schema

## Kafka Topics Configuration

### Topics Defined
1. **task-events** (3 partitions) - Task lifecycle events (create/update/delete/complete)
2. **reminders** (1 partition) - Reminder notifications from cron binding
3. **task-updates** (3 partitions) - Task field modifications and status changes

### Event Schemas
- All events include: event_id, event_type, task_id, user_id, timestamp, metadata
- task-events: includes task_data, old_data (for updates/deletes)
- reminders: includes reminder_time, notification_type, task_summary
- task-updates: includes update_type, changes (field-level diffs)

### Retention Policy
- All topics: 7 days (604800000 ms)
- Compression: Snappy
- Cleanup policy: delete (not compaction)

## Dapr Component Patterns

### Pub/Sub (Kafka)
- Component name: `pubsub-kafka`
- Type: `pubsub.kafka`
- Broker address: `todo-kafka-kafka-bootstrap.kafka.svc.cluster.local:9092`
- Consumer group: `todo-app-consumer-group`
- Subscriptions: 3 topics with dead-letter queues enabled
- Publishing endpoint: `POST /v1.0/publish/{pubsub-name}/{topic}`
- Subscription routes: `/events/task-events`, `/events/reminders`, `/events/task-updates`

### State Store (PostgreSQL)
- Component name: `statestore-postgresql`
- Type: `state.postgresql`
- Table: `dapr_state` (auto-created)
- Connection: secretKeyRef to `todo-app-secrets/DATABASE_URL`
- Features: ETags for concurrency, prepared statements, connection pooling
- State API: `GET/POST/DELETE /v1.0/state/{state-store-name}/{key}`

### Bindings (Cron)
- Component name: `binding-cron`
- Type: `bindings.cron`
- Schedule: `@every 5m` (configurable)
- Direction: input (triggers application)
- Handler endpoint: `POST /bindings/binding-cron`
- Use case: Check for due reminders every 5 minutes

### Secrets (Kubernetes)
- Component name: `secrets-kubernetes`
- Type: `secretstores.kubernetes`
- Scopes: todo-backend, todo-frontend
- Secrets: todo-app-secrets (DATABASE_URL, BETTER_AUTH_SECRET, COHERE_API_KEY)
- RBAC: ServiceAccount + Role + RoleBinding for secret access
- API: `GET /v1.0/secrets/{secret-store-name}/{secret-name}/{key}`

## Dapr Configuration Settings

### Global Config (dapr-config.yaml)
- Tracing: enabled, 100% sampling (reduce to 10% in production)
- Metrics: enabled, Prometheus endpoint on port 9090
- Logging: API logging enabled, health checks omitted
- Zipkin endpoint: `http://zipkin.monitoring.svc.cluster.local:9411/api/v2/spans`

### Sidecar Annotations (for Helm deployments)
```yaml
dapr.io/enabled: "true"
dapr.io/app-id: "todo-backend"
dapr.io/app-port: "8000"
dapr.io/app-protocol: "http"
dapr.io/config: "dapr-config"
dapr.io/log-level: "info"
dapr.io/enable-metrics: "true"
dapr.io/metrics-port: "9090"
```

## Backend Integration Patterns

### Publishing Events (Python/FastAPI)
```python
import httpx

async def publish_event(pubsub_name: str, topic: str, event_data: dict):
    dapr_port = os.getenv("DAPR_HTTP_PORT", "3500")
    url = f"http://localhost:{dapr_port}/v1.0/publish/{pubsub_name}/{topic}"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=event_data)
        response.raise_for_status()
    return response.status_code
```

### Subscribing to Events
```python
from dapr.ext.fastapi import DaprApp

@dapr_app.subscribe(pubsub="pubsub-kafka", topic="task-events")
async def task_events_handler(event: dict):
    # Process event
    return {"status": "SUCCESS"}
```

### State Management
```python
# Save state
state = [{"key": f"task-{task_id}", "value": task_data}]
url = f"http://localhost:{dapr_port}/v1.0/state/{state_store_name}"
response = await client.post(url, json=state)

# Get state
url = f"http://localhost:{dapr_port}/v1.0/state/{state_store_name}/{key}"
response = await client.get(url)
```

### Cron Handler
```python
@app.post("/bindings/binding-cron")
async def handle_reminder_cron(request: Request):
    # Query tasks with due reminders
    # Publish reminder events
    return {"status": "SUCCESS", "processed": count}
```

## Security Best Practices

1. **Secrets**: Never commit to Git, use Kubernetes Secrets with RBAC
2. **Connection Strings**: Always use secretKeyRef, not direct values
3. **TLS**: Enable for production (Kafka, PostgreSQL, Ingress)
4. **Scopes**: Restrict component access to specific app-ids
5. **RBAC**: Least-privilege roles for secret access

## Deployment Flow

### Minikube
1. Install Dapr: `dapr init -k --runtime-version 1.14`
2. Deploy Kafka: Strimzi operator + Kafka cluster
3. Apply Dapr components: `kubectl apply -f k8s/dapr/components/`
4. Apply Dapr config: `kubectl apply -f k8s/dapr/config/`
5. Deploy application with Helm (sidecar annotations)

### OKE
1. Provision OKE cluster (4 OCPU, 24GB RAM)
2. Install Dapr via Helm
3. Deploy Kafka cluster
4. Apply components and config to `todo` namespace
5. Deploy application with production values

## Validation Commands

```bash
# Verify Dapr status
dapr status -k

# Check components
kubectl get components -n default

# Validate YAML
python -c "import yaml; yaml.safe_load_all(open('file.yaml'))"

# Test Dapr sidecar health
curl http://localhost:3500/v1.0/healthz

# Check metrics
curl http://localhost:9090/metrics
```

## Known Patterns & Lessons

### Component Files
- Each component is a separate YAML file for modularity
- Include comprehensive comments for production configuration
- Reference official Dapr docs for metadata options
- Always validate YAML syntax before deployment

### Event Schemas
- Define schemas in comments for documentation
- Include metadata: source, version, trace_id
- Use UUID v4 for event_id and trace_id
- ISO-8601 format for all timestamps

### Migration Strategy
- Replace direct Kafka clients with Dapr Pub/Sub API
- Replace direct PostgreSQL queries with Dapr State Store
- Replace cron libraries with Dapr Bindings
- Use feature flags for gradual rollout

### Error Handling
- Configure dead-letter queues for all subscriptions
- Implement retry with exponential backoff
- Track event_id for idempotency
- Log all errors with trace_id for debugging

## Next Steps (Pending Tasks)

### T015-T017: Docker & Image Foundation
- Create multi-stage Dockerfiles for frontend and backend
- Test builds locally before deployment

### T018-T033: Helm Chart Foundation
- Create Helm chart with Dapr sidecar annotations
- Template all Kubernetes manifests
- Environment-specific values (Minikube, OKE)

### Backend Implementation
- Implement Dapr HTTP client service
- Add event publishing to CRUD operations
- Create event consumers for reminders and audit
- Update API endpoints to use Dapr State Store

## Reference Links
- [Dapr Pub/Sub Spec](https://docs.dapr.io/reference/components-reference/supported-pubsub/)
- [Dapr State Store Spec](https://docs.dapr.io/reference/components-reference/supported-state-stores/)
- [Dapr Bindings Spec](https://docs.dapr.io/reference/components-reference/supported-bindings/)
- [Dapr Secrets Spec](https://docs.dapr.io/reference/components-reference/supported-secret-stores/)
