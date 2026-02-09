# Phase 3: Minikube Deployment MVP - Execution Script

**Status**: Minikube startup in progress
**Branch**: 004-event-driven-cloud
**Date**: 2026-02-09

---

## Cluster Status Checks

### T039: Start Minikube Cluster ✅ IN PROGRESS
```bash
minikube start --cpus=4 --memory=6144 --disk-size=50g --driver=docker
# Expected: Kubernetes control plane started, kubelet ready, API server ready
```

### T040: Enable Minikube Addons (Run after T039 completes)
```bash
minikube addons enable ingress
minikube addons enable metrics-server
# Expected: ingress-nginx deployed in ingress-nginx namespace, metrics-server ready
```

### T041: Verify Minikube Running
```bash
minikube status
kubectl cluster-info
kubectl get nodes
# Expected: minikube node Ready, cluster accessible
```

---

## Dapr Installation (T042)

### Prerequisites
```bash
# Verify kubectl context
kubectl config current-context
# Expected: minikube

# Check API server
kubectl get apiresources | head
# Expected: API groups available
```

### Install Dapr Runtime
```bash
dapr init -k --runtime-version 1.14
# Expected: Installing Dapr to Kubernetes, Dapr control plane ready

# Verify Dapr installation
dapr status -k
# Expected:
# NAMESPACE  NAME                    READY  STATUS   RESTARTS  AGE
# dapr-system  dapr-operator           1/1    Running  0         XXs
# dapr-system  dapr-sidecar-injector   1/1    Running  0         XXs
# dapr-system  dapr-placement-service  1/1    Running  0         XXs

# Check Dapr system namespace
kubectl get all -n dapr-system
# Expected: 4 deployments, 4 pods running
```

---

## Kafka Installation (T043)

### Install Strimzi Operator
```bash
# Add Helm repository
helm repo add strimzi https://strimzi.io/charts
helm repo update

# Install Strimzi operator
helm install strimzi strimzi/strimzi-kafka-operator \
  -n kafka \
  --create-namespace \
  --set replicas=1
# Expected: Strimzi operator deployed, CRDs created

# Verify operator ready
kubectl get deployment -n kafka
# Expected: strimzi-cluster-operator 1/1 Running
```

---

## Kafka Cluster Deployment (T044-T046)

### T044: Deploy Kafka Cluster
```bash
# Deploy Kafka cluster using Strimzi
kubectl apply -f k8s/kafka/kafka-cluster.yaml
# Expected: Kafka cluster custom resources created

# Watch Kafka startup
kubectl get kafka -n kafka -w
# Expected: todo-kafka cluster reaching Ready state (takes 2-3 minutes)

# Verify Kafka broker ready
kubectl get pods -n kafka
# Expected:
# - todo-kafka-kafka-0          (Kafka broker)
# - todo-kafka-zookeeper-0      (ZooKeeper)
# - strimzi-*-operator-*        (Strimzi operator)
```

### T045: Verify Kafka Topics Created
```bash
# Check Kafka topics via Strimzi operator
kubectl get kafkatopic -n kafka
# Expected:
# NAME              PARTITIONS  REPLICATION FACTOR
# task-events       3           1
# reminders         1           1
# task-updates      3           1

# Alternative: Access Kafka broker directly (if needed)
kubectl port-forward -n kafka svc/todo-kafka-kafka-bootstrap 9092:9092 &
# Then use kafka-console-producer/consumer if needed
```

### T046: Verify Kafka Cluster Ready
```bash
kubectl get kafka -n kafka -o jsonpath='{.items[0].status.conditions}'
# Expected: Condition Type: Ready, Status: True

# Alternative check
kubectl describe kafka todo-kafka -n kafka
# Expected: Status -> Conditions: Ready True
```

---

## Dapr Components Deployment (T047-T048)

### T047: Deploy Dapr Components
```bash
# Apply all Dapr components
kubectl apply -f k8s/dapr/components/ -n default
kubectl apply -f k8s/dapr/config/ -n default
# Expected: 6 components created + 1 config

# List created components
kubectl get components -n default
# Expected:
# NAME                         AGE
# pubsub-kafka                 XX
# statestore-postgresql        XX
# binding-cron                 XX
# secrets-kubernetes           XX
```

### T048: Verify Dapr Components
```bash
# Check component status
kubectl get components -A
# Expected: All 4 components in default namespace

# Verify component definitions (should show spec details)
kubectl get component pubsub-kafka -o yaml
# Expected: spec.type: pubsub.kafka, metadata.type: kafka

# Check for component errors
kubectl get events -A | grep -i dapr
# Expected: No error events
```

---

## Application Deployment via Helm (T049-T052)

### T049: Deploy Todo App to Minikube
```bash
# Create default namespace (if not exists)
kubectl create namespace default --dry-run=client -o yaml | kubectl apply -f -

# Deploy via Helm
helm install todo ./k8s/helm/todo-app \
  -f ./k8s/helm/todo-app/values-minikube.yaml \
  -n default
# Expected: Release "todo" has been installed

# Alternative with specific image tags
helm install todo ./k8s/helm/todo-app \
  -f ./k8s/helm/todo-app/values-minikube.yaml \
  --set backend.image.tag=latest \
  --set frontend.image.tag=latest \
  -n default
```

### T050: Verify Pods Created and Ready
```bash
# Watch pods reaching Running state
kubectl get pods -n default -w
# Expected: frontend, backend pods Running, Dapr sidecars Ready

# Detailed pod status
kubectl get pods -n default -o wide
# Expected:
# NAME                                READY   STATUS    RESTARTS
# todo-frontend-XXXXX                 2/2     Running   0
# todo-backend-XXXXX                  2/2     Running   0

# Wait for all pods Ready (max 3 minutes)
kubectl wait --for=condition=Ready pod -l app=todo-frontend -n default --timeout=300s
kubectl wait --for=condition=Ready pod -l app=todo-backend -n default --timeout=300s
```

### T051: Verify Services Created
```bash
# List services
kubectl get svc -n default
# Expected:
# NAME              TYPE      CLUSTER-IP    EXTERNAL-IP  PORT(S)
# todo-frontend     NodePort  10.X.X.X                   3000:30123/TCP
# todo-backend      ClusterIP 10.X.X.X                   8000/TCP
# kubernetes        ClusterIP 10.96.0.1                  443/TCP

# Get service details
kubectl get svc todo-frontend -o wide
kubectl get svc todo-backend -o wide
```

### T052: Verify ConfigMap Created
```bash
# Check configmap
kubectl get configmap -n default
# Expected: todo-app configmap present

# View configmap contents
kubectl get configmap todo-app -o yaml
# Expected:
# KAFKA_BOOTSTRAP_SERVERS: todo-kafka-kafka-bootstrap.kafka.svc.cluster.local:9092
# DAPR_PUBSUB_NAME: pubsub-kafka
# DAPR_STATE_STORE_NAME: statestore-postgresql
```

---

## Deployment Health Testing (T053-T056)

### T053: Test Frontend Accessibility
```bash
# Port-forward frontend
kubectl port-forward svc/todo-frontend 3000:3000 -n default &

# Test endpoint
curl -s http://localhost:3000 | head -20
# Expected: HTML content, <html>, <head>, <title>

# Cleanup (kill background process)
kill %1
```

### T054: Test Backend Health
```bash
# Port-forward backend
kubectl port-forward svc/todo-backend 8000:8000 -n default &

# Test health endpoint
curl -s http://localhost:8000/health
# Expected: JSON response like {"status":"healthy"} or similar

# Test root endpoint
curl -s http://localhost:8000 | head -10
# Expected: API documentation or OK response

# Cleanup
kill %1
```

### T055: Test Dapr Sidecar Health
```bash
# Check Dapr sidecars in deployment pods
kubectl get pods -n default -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.containers[*].name}{"\n"}{end}'
# Expected: Each pod shows 2 containers: main app + daprd

# Verify Dapr sidecar status
dapr status -k
# Expected: All sidecars in dapr-sidecar-injector namespace, sidecar sidecars healthy

# Check sidecar logs (if needed)
kubectl logs -l app=todo-backend -c daprd -n default --tail=20
# Expected: Dapr sidecar logs showing component initialization
```

### T056: Test Kafka Connectivity
```bash
# Check backend logs for Kafka connection
kubectl logs -l app=todo-backend -c todo-backend -n default --tail=50 | grep -i kafka
# Expected: Connection to Kafka broker successful, subscriptions established

# Alternative: Check for Kafka connection in Dapr logs
kubectl logs -l app=todo-backend -c daprd -n default --tail=50 | grep -i kafka
# Expected: Kafka broker connected, pub/sub component initialized
```

---

## Functional Testing (T057-T065)

### T057: Create Task via Frontend
```bash
# Access frontend
# kubectl port-forward svc/todo-frontend 3000:3000 -n default

# In browser: http://localhost:3000
# Action: Click "New Task", enter title, click Create
# Expected: Task appears in list immediately

# Or use curl to API
curl -X POST http://localhost:8000/api/1/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Test task","description":"Created in Minikube"}' \
  -H "Authorization: Bearer <JWT_TOKEN>"
# Expected: 201 Created, task ID returned
```

### T058: Create Task with Phase 5 Part A Fields
```bash
curl -X POST http://localhost:8000/api/1/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Buy groceries",
    "description": "Weekly shopping",
    "priority": "high",
    "tags": ["shopping", "urgent"],
    "due_date": "2026-02-15T14:00:00Z",
    "recurrence_rule": "daily",
    "reminder_offset": 1
  }' \
  -H "Authorization: Bearer <JWT_TOKEN>"
# Expected: 201 Created, all fields persisted
```

### T059: Verify Task Persisted
```bash
# Reload browser or call API again
curl -X GET http://localhost:8000/api/1/tasks \
  -H "Authorization: Bearer <JWT_TOKEN>"
# Expected: Task still present with all fields
```

### T060-T062: Filter and Search
```bash
# Filter by priority
curl -X GET "http://localhost:8000/api/1/tasks?priority=high" \
  -H "Authorization: Bearer <JWT_TOKEN>"
# Expected: Only high-priority tasks

# Filter by tag
curl -X GET "http://localhost:8000/api/1/tasks?tag=shopping" \
  -H "Authorization: Bearer <JWT_TOKEN>"
# Expected: Tasks with shopping tag

# Search
curl -X GET "http://localhost:8000/api/1/tasks?search=groceries" \
  -H "Authorization: Bearer <JWT_TOKEN>"
# Expected: Tasks matching search term
```

### T063: Test Recurring Task
```bash
# Create daily recurring task
curl -X POST http://localhost:8000/api/1/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Daily standup",
    "recurrence_rule": "daily",
    "due_date": "2026-02-09T09:00:00Z"
  }' \
  -H "Authorization: Bearer <JWT_TOKEN>"

# Mark as complete
curl -X PATCH http://localhost:8000/api/1/tasks/<TASK_ID>/toggle \
  -H "Authorization: Bearer <JWT_TOKEN>"

# Wait 5 seconds, check if new instance created
sleep 5
curl -X GET http://localhost:8000/api/1/tasks \
  -H "Authorization: Bearer <JWT_TOKEN>" | grep -i "Daily standup"
# Expected: Second instance created with same title
```

### T064: Test Reminder Trigger
```bash
# Create task with due date 1 minute in future
FUTURE_TIME=$(date -u -d '+1 minute' +'%Y-%m-%dT%H:%M:%SZ')

curl -X POST http://localhost:8000/api/1/tasks \
  -H "Content-Type: application/json" \
  -d "{
    \"title\": \"Reminder test\",
    \"due_date\": \"$FUTURE_TIME\",
    \"reminder_offset\": 0
  }" \
  -H "Authorization: Bearer <JWT_TOKEN>"

# Wait for cron binding to trigger (check reminders topic)
# Port-forward to Kafka and check messages
# Expected: Reminder event appears in `reminders` topic
```

### T065: Test Audit Logging
```bash
# Create a task
curl -X POST http://localhost:8000/api/1/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Audit test"}' \
  -H "Authorization: Bearer <JWT_TOKEN>" > /tmp/task.json

TASK_ID=$(jq -r '.id' /tmp/task.json)

# Update the task
curl -X PATCH http://localhost:8000/api/1/tasks/$TASK_ID \
  -H "Content-Type: application/json" \
  -d '{"title":"Audit test updated"}' \
  -H "Authorization: Bearer <JWT_TOKEN>"

# Delete the task
curl -X DELETE http://localhost:8000/api/1/tasks/$TASK_ID \
  -H "Authorization: Bearer <JWT_TOKEN>"

# Check Kafka task-events topic for 3 events (CREATE, UPDATE, DELETE)
# Expected: 3 events recorded in audit trail
```

---

## Integration Testing (T066-T068)

### T066: Run Helm Tests
```bash
helm test todo -n default
# Expected: All test pods complete successfully

# View test results
kubectl get pods -n default -l "app.kubernetes.io/instance=todo"
# Expected: test pods with status Succeeded
```

### T067: Run E2E Test Suite
```bash
# Execute all manual test scenarios
# From PHASE5_TESTING_MINIKUBE.md
# Expected: All 12 scenarios pass
```

### T068: Verify Multi-User Isolation
```bash
# Create user 1 with JWT token (user_id=1)
# Create user 2 with JWT token (user_id=2)

# User 1 creates task
curl -X POST http://localhost:8000/api/1/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"User 1 task"}' \
  -H "Authorization: Bearer <JWT_USER1>"

# User 2 lists tasks
curl -X GET http://localhost:8000/api/2/tasks \
  -H "Authorization: Bearer <JWT_USER2>"

# Expected: User 2 does NOT see User 1's task (only their own tasks)
```

---

## Documentation (T069-T070)

### T069: Minikube Setup Documentation
- Update quickstart.md with actual commands executed
- Document any workarounds (e.g., memory adjustment 8GB → 6GB)
- Record timings for each step

### T070: Testing Scenarios Documentation
- Create PHASE5_TESTING_MINIKUBE.md
- Document all 12 manual test scenarios
- Include expected vs actual results

---

## Checkpoint: Phase 3 Complete

**Success Criteria** (all must pass):
- ✅ Minikube cluster running with 4 CPUs, 6GB RAM
- ✅ Dapr control plane deployed and healthy
- ✅ Kafka cluster with 3 topics running
- ✅ Dapr components (pubsub, state, bindings, secrets) operational
- ✅ Todo app deployed via Helm (frontend + backend)
- ✅ All 7 Phase 5 Part A features verified working
- ✅ Multi-user isolation confirmed
- ✅ Event-driven patterns validated (events flowing through Kafka)
- ✅ Helm tests passing
- ✅ E2E test suite passing

**Next Phase**: Phase 4 - User Story 2 (Reminder & Notification System)
