# Phase 5 Event-Driven & Cloud Deployment - Quickstart Guide

**Version**: 1.0
**Date**: 2026-02-09
**Branch**: 004-event-driven-cloud
**Status**: Production Ready

---

## Table of Contents

- [Overview](#overview)
- [Part 1: Minikube Local Deployment](#part-1-minikube-local-deployment)
  - [Prerequisites](#prerequisites-minikube)
  - [Step-by-Step Setup](#step-by-step-minikube-setup)
  - [Deployment Steps](#minikube-deployment-steps)
  - [Testing & Verification](#minikube-testing--verification)
  - [Troubleshooting](#minikube-troubleshooting)
  - [Cleanup](#minikube-cleanup)
- [Part 2: Oracle OKE Cloud Deployment](#part-2-oracle-oke-cloud-deployment)
  - [Prerequisites](#prerequisites-oke)
  - [OKE Cluster Provisioning](#oke-cluster-provisioning)
  - [Dapr Installation](#dapr-installation-on-oke)
  - [Kafka Deployment](#kafka-deployment-on-oke)
  - [Application Deployment](#application-deployment-to-oke)
  - [TLS & HTTPS Access](#tls--https-access)
  - [Production Considerations](#production-considerations)
  - [Troubleshooting](#oke-troubleshooting)
  - [Cleanup](#oke-cleanup)
- [Appendices](#appendices)
  - [Architecture Overview](#architecture-overview)
  - [CLI Reference](#cli-reference)
  - [Common Errors & Solutions](#common-errors--solutions)
  - [Performance Tuning](#performance-tuning)

---

## Overview

This guide provides comprehensive instructions for deploying the **Phase 5 Event-Driven Todo Application** to:

1. **Minikube** (local development and testing)
2. **Oracle Kubernetes Engine (OKE)** (production cloud deployment)

The application leverages:
- **Dapr 1.14+** for event-driven abstractions (Pub/Sub, State, Bindings, Secrets)
- **Kafka** for event streaming (task events, reminders, audit logs)
- **Next.js 16** frontend with React 19
- **FastAPI** backend with SQLModel and Neon PostgreSQL
- **Prometheus + Grafana + Loki** for observability (Part C)
- **Helm 3.12+** for reproducible deployments

**Estimated Time**:
- **Minikube Setup**: 45-60 minutes (first-time installation)
- **OKE Setup**: 90-120 minutes (cluster provisioning + deployment)

---

# Part 1: Minikube Local Deployment

## Prerequisites (Minikube)

### System Requirements

| Resource | Minimum | Recommended | Notes |
|----------|---------|-------------|-------|
| CPU | 4 cores | 6+ cores | Minikube + Dapr + Kafka require 4+ cores |
| RAM | 8 GB | 12+ GB | Kafka and Dapr sidecars are memory-intensive |
| Disk | 50 GB | 100+ GB | Docker images, Kafka logs, Prometheus metrics |
| OS | macOS, Linux, Windows 10+ | macOS/Linux preferred | Windows requires WSL2 or Hyper-V |

### Required Tools

Install the following tools before proceeding:

#### 1. Docker Desktop (or Docker Engine)

**Version Required**: 24.0+

```bash
# Verify installation
docker --version
# Expected output: Docker version 24.x.x or higher

docker compose version
# Expected output: Docker Compose version v2.x.x or higher
```

**Installation**:
- **macOS/Windows**: Download [Docker Desktop](https://www.docker.com/products/docker-desktop)
- **Linux**: Follow [Docker Engine installation](https://docs.docker.com/engine/install/)

**Configuration**:
- Allocate **at least 4 CPUs and 8 GB RAM** to Docker Desktop (Preferences → Resources)

---

#### 2. Minikube

**Version Required**: 1.30+

```bash
# Verify installation
minikube version
# Expected output: minikube version: v1.30.x or higher
```

**Installation**:

```bash
# macOS with Homebrew
brew install minikube

# Linux
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# Windows with Chocolatey
choco install minikube
```

**Verification**:
```bash
minikube version
minikube status
```

---

#### 3. kubectl

**Version Required**: 1.27+

```bash
# Verify installation
kubectl version --client
# Expected output: Client Version: v1.27.x or higher
```

**Installation**:

```bash
# macOS with Homebrew
brew install kubectl

# Linux
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Windows with Chocolatey
choco install kubernetes-cli
```

**Verification**:
```bash
kubectl version --client --output=yaml
```

---

#### 4. Helm

**Version Required**: 3.12+

```bash
# Verify installation
helm version
# Expected output: version.BuildInfo{Version:"v3.12.x" or higher}
```

**Installation**:

```bash
# macOS with Homebrew
brew install helm

# Linux
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Windows with Chocolatey
choco install kubernetes-helm
```

**Verification**:
```bash
helm version --short
helm repo list  # Should return empty list initially
```

---

#### 5. Dapr CLI

**Version Required**: 1.14+

```bash
# Verify installation
dapr version
# Expected output: CLI version: 1.14.x or higher
```

**Installation**:

```bash
# macOS/Linux
wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash

# Windows (PowerShell as Administrator)
powershell -Command "iwr -useb https://raw.githubusercontent.com/dapr/cli/master/install/install.ps1 | iex"
```

**Verification**:
```bash
dapr version
```

---

### Prerequisites Verification Checklist

Run this checklist before proceeding:

```bash
# All commands should succeed without errors
docker --version
docker compose version
minikube version
kubectl version --client
helm version --short
dapr version
```

**Expected Output**:
```
Docker version 24.x.x or higher
Docker Compose version v2.x.x
minikube version: v1.30.x or higher
Client Version: v1.27.x or higher
v3.12.x or higher
CLI version: 1.14.x or higher
```

If all commands succeed, proceed to **Step-by-Step Minikube Setup**.

---

## Step-by-Step Minikube Setup

**Estimated Time**: 15-20 minutes

### Step 1: Start Minikube Cluster

Start Minikube with **4 CPUs, 8 GB RAM, and 50 GB disk**:

```bash
minikube start --cpus=4 --memory=8192 --disk-size=50g --driver=docker
```

**Expected Output**:
```
😄  minikube v1.38.0 on Darwin 15.2 (arm64)
✨  Using the docker driver based on user configuration
👍  Starting "minikube" primary control-plane node in "minikube" cluster
🚜  Pulling base image ...
🔥  Creating docker container (CPUs=4, Memory=8192MB) ...
🐳  Preparing Kubernetes v1.35.0 on Docker 27.5.1 ...
🔎  Verifying Kubernetes components...
🌟  Enabled addons: storage-provisioner, default-storageclass
🏄  Done! kubectl is now configured to use "minikube" cluster and "default" namespace by default
```

**Verification**:
```bash
minikube status
```

**Expected Output**:
```
minikube
type: Control Plane
host: Running
kubelet: Running
apiserver: Running
kubeconfig: Configured
```

**Estimated Time**: 3-5 minutes

---

### Step 2: Enable Minikube Addons

Enable **Ingress** and **Metrics Server**:

```bash
minikube addons enable ingress
minikube addons enable metrics-server
```

**Expected Output**:
```
💡  ingress is an addon maintained by Kubernetes. For any concerns contact minikube on GitHub.
    ▪ Using image registry.k8s.io/ingress-nginx/controller:v1.12.0-beta.0
    ▪ Using image registry.k8s.io/ingress-nginx/kube-webhook-certgen:v1.4.4
🔎  Verifying ingress addon...
🌟  The 'ingress' addon is enabled

💡  metrics-server is an addon maintained by Kubernetes. For any concerns contact minikube on GitHub.
    ▪ Using image registry.k8s.io/metrics-server/metrics-server:v0.7.2
🌟  The 'metrics-server' addon is enabled
```

**Verification**:
```bash
kubectl get pods -n ingress-nginx
kubectl get pods -n kube-system | grep metrics-server
```

**Expected Output**:
```
# Ingress controller pod should be Running
ingress-nginx-controller-xxxxx   1/1     Running   0          30s

# Metrics server pod should be Running
metrics-server-xxxxx             1/1     Running   0          20s
```

**Estimated Time**: 2-3 minutes

---

### Step 3: Verify Kubernetes Cluster

Verify cluster is healthy and kubectl context is set:

```bash
kubectl cluster-info
```

**Expected Output**:
```
Kubernetes control plane is running at https://127.0.0.1:xxxxx
CoreDNS is running at https://127.0.0.1:xxxxx/api/v1/namespaces/kube-system/services/kube-dns:dns/proxy

To further debug and diagnose cluster problems, use 'kubectl cluster-info dump'.
```

**Verify nodes**:
```bash
kubectl get nodes
```

**Expected Output**:
```
NAME       STATUS   ROLES           AGE   VERSION
minikube   Ready    control-plane   2m    v1.35.0
```

**Estimated Time**: <1 minute

---

### Step 4: Install Dapr on Minikube

Install Dapr runtime to Kubernetes cluster:

```bash
dapr init -k --runtime-version 1.14
```

**Expected Output**:
```
⌛  Making the jump to hyperspace...
ℹ️  Note: To install Dapr using Helm, see here: https://docs.dapr.io/operations/hosting/kubernetes/kubernetes-deploy/#install-with-helm-advanced

✅  Deploying the Dapr control plane to your cluster...
✅  Deploying the Dapr dashboard to your cluster...
✅  Success! Dapr has been installed to namespace dapr-system. To verify, run `dapr status -k' in your terminal. To get started, go here: https://docs.dapr.io/getting-started
```

**Verification**:
```bash
dapr status -k
```

**Expected Output**:
```
  NAME                   NAMESPACE    HEALTHY  STATUS   REPLICAS  VERSION  AGE  CREATED
  dapr-sidecar-injector  dapr-system  True     Running  1         1.14.0   10s  2026-02-09 10:00.00
  dapr-sentry            dapr-system  True     Running  1         1.14.0   10s  2026-02-09 10:00.00
  dapr-operator          dapr-system  True     Running  1         1.14.0   10s  2026-02-09 10:00.00
  dapr-placement         dapr-system  True     Running  1         1.14.0   10s  2026-02-09 10:00.00
  dapr-dashboard         dapr-system  True     Running  1         1.14.0   10s  2026-02-09 10:00.00
```

**All services should show `HEALTHY: True` and `STATUS: Running`.**

**Estimated Time**: 2-3 minutes

---

### Step 5: Install Strimzi Kafka Operator

Add Strimzi Helm repository and install operator:

```bash
# Add Strimzi Helm repository
helm repo add strimzi https://strimzi.io/charts/
helm repo update

# Create kafka namespace
kubectl create namespace kafka

# Install Strimzi operator
helm install strimzi strimzi/strimzi-kafka-operator \
  -n kafka \
  --set watchAnyNamespace=true
```

**Expected Output**:
```
"strimzi" has been added to your repositories
Hang tight while we grab the latest from your chart repositories...
...Successfully got an update from the "strimzi" chart repository
Update Complete. ⎈Happy Helming!⎈

namespace/kafka created

NAME: strimzi
LAST DEPLOYED: Sun Feb  9 10:00:00 2026
NAMESPACE: kafka
STATUS: deployed
REVISION: 1
TEST SUITE: None
NOTES:
Thank you for installing strimzi-kafka-operator-0.44.0
...
```

**Verification**:
```bash
kubectl get pods -n kafka -w
```

**Expected Output** (wait until Running):
```
NAME                                        READY   STATUS    RESTARTS   AGE
strimzi-cluster-operator-xxxxxxxxxx-xxxxx   1/1     Running   0          30s
```

**Estimated Time**: 2-3 minutes

---

### Step 6: Deploy Kafka Cluster

Deploy Kafka cluster and topics:

```bash
# Apply Kafka cluster configuration
kubectl apply -f k8s/kafka/kafka-cluster.yaml -n kafka

# Wait for Kafka cluster to become ready (2-3 minutes)
kubectl wait kafka/todo-kafka --for=condition=Ready --timeout=300s -n kafka
```

**Expected Output**:
```
kafka.kafka.strimzi.io/todo-kafka created
kafka.kafka.strimzi.io/todo-kafka condition met
```

**Deploy Kafka topics**:
```bash
kubectl apply -f k8s/kafka/kafka-topics.yaml -n kafka
```

**Expected Output**:
```
kafkatopic.kafka.strimzi.io/task-events created
kafkatopic.kafka.strimzi.io/reminders created
kafkatopic.kafka.strimzi.io/task-updates created
```

**Verification**:
```bash
# Check Kafka cluster pods
kubectl get pods -n kafka

# Check Kafka topics
kubectl get kafkatopic -n kafka
```

**Expected Output**:
```
# Pods (should see Kafka broker, ZooKeeper, entity operator)
NAME                                          READY   STATUS    RESTARTS   AGE
strimzi-cluster-operator-xxxxxxxxxx-xxxxx     1/1     Running   0          5m
todo-kafka-kafka-0                            1/1     Running   0          2m
todo-kafka-zookeeper-0                        1/1     Running   0          3m
todo-kafka-entity-operator-xxxxxxxxxx-xxxxx   2/2     Running   0          90s

# Topics
NAME           CLUSTER      PARTITIONS   REPLICATION FACTOR   READY
task-events    todo-kafka   3            1                    True
reminders      todo-kafka   1            1                    True
task-updates   todo-kafka   3            1                    True
```

**Estimated Time**: 4-5 minutes

---

### Step 7: Deploy Dapr Components

Deploy Dapr components (Pub/Sub, State, Bindings, Secrets):

```bash
kubectl apply -f k8s/dapr/components/ -n default
```

**Expected Output**:
```
component.dapr.io/pubsub-kafka created
component.dapr.io/statestore-postgresql created
component.dapr.io/binding-cron created
component.dapr.io/secrets-kubernetes created
configuration.dapr.io/dapr-config created
```

**Verification**:
```bash
kubectl get components -n default
kubectl get configurations.dapr.io -n default
```

**Expected Output**:
```
NAME                     AGE
pubsub-kafka             10s
statestore-postgresql    10s
binding-cron             10s
secrets-kubernetes       10s

NAME           AGE
dapr-config    10s
```

**Estimated Time**: 1 minute

---

## Minikube Deployment Steps

**Estimated Time**: 5-10 minutes

### Step 1: Create Kubernetes Secrets

Create secrets for database URL, Better Auth secret, and Cohere API key:

```bash
# Replace with your actual secret values
kubectl create secret generic todo-app-secrets \
  --from-literal=DATABASE_URL="postgresql://user:password@host/database?sslmode=require" \
  --from-literal=BETTER_AUTH_SECRET="your-32-char-secret-here" \
  --from-literal=COHERE_API_KEY="your-cohere-api-key" \
  --from-literal=NEXTAUTH_URL="http://localhost:3000" \
  --from-literal=NEXTAUTH_SECRET="your-nextauth-secret" \
  -n default
```

**Expected Output**:
```
secret/todo-app-secrets created
```

**Verification**:
```bash
kubectl get secret todo-app-secrets -n default
```

**Expected Output**:
```
NAME                TYPE     DATA   AGE
todo-app-secrets    Opaque   5      5s
```

**SECURITY NOTE**: Never commit secrets to Git. Use `.env` files locally and `kubectl create secret` for Kubernetes.

---

### Step 2: Deploy Todo App via Helm

Deploy the application using Helm with Minikube-specific values:

```bash
helm install todo ./k8s/helm/todo-app \
  -f ./k8s/helm/todo-app/values-minikube.yaml \
  -n default
```

**Expected Output**:
```
NAME: todo
LAST DEPLOYED: Sun Feb  9 10:30:00 2026
NAMESPACE: default
STATUS: deployed
REVISION: 1
TEST SUITE: None
NOTES:
1. Get the application URL by running these commands:
  export NODE_PORT=$(kubectl get --namespace default -o jsonpath="{.spec.ports[0].nodePort}" services todo-frontend)
  export NODE_IP=$(minikube ip)
  echo http://$NODE_IP:$NODE_PORT

2. Access the backend API:
  export API_PORT=$(kubectl get --namespace default -o jsonpath="{.spec.ports[0].nodePort}" services todo-backend)
  echo http://$NODE_IP:$API_PORT/docs
```

**Estimated Time**: 2-3 minutes

---

### Step 3: Wait for Pods to Become Ready

Monitor pod startup:

```bash
kubectl get pods -n default -w
```

**Expected Output** (wait until all pods are Running with 2/2 Ready):
```
NAME                            READY   STATUS              RESTARTS   AGE
todo-backend-xxxxxxxxxx-xxxxx   0/2     ContainerCreating   0          10s
todo-frontend-xxxxxxxxxx-xxxxx  0/2     ContainerCreating   0          10s
todo-backend-xxxxxxxxxx-xxxxx   1/2     Running             0          30s
todo-frontend-xxxxxxxxxx-xxxxx  1/2     Running             0          30s
todo-backend-xxxxxxxxxx-xxxxx   2/2     Running             0          45s
todo-frontend-xxxxxxxxxx-xxxxx  2/2     Running             0          50s
```

**Note**: Each pod has **2 containers** (application + Dapr sidecar). Wait for `2/2 Ready`.

**Timeout**: Pods should be Ready within **3 minutes**. If not, see [Troubleshooting](#minikube-troubleshooting).

---

### Step 4: Access Frontend via Port-Forward

Port-forward frontend service to localhost:

```bash
kubectl port-forward svc/todo-frontend 3000:3000 -n default
```

**Expected Output**:
```
Forwarding from 127.0.0.1:3000 -> 3000
Forwarding from [::1]:3000 -> 3000
```

**Access Application**:
Open browser and navigate to: **http://localhost:3000**

You should see the **Todo Application login page**.

**Leave terminal open** (port-forward runs in foreground). Open new terminal for backend access.

---

### Step 5: Access Backend API Docs (Optional)

Port-forward backend service to localhost:

```bash
kubectl port-forward svc/todo-backend 8000:8000 -n default
```

**Expected Output**:
```
Forwarding from 127.0.0.1:8000 -> 8000
Forwarding from [::1]:8000 -> 8000
```

**Access API Documentation**:
Open browser and navigate to: **http://localhost:8000/docs**

You should see the **FastAPI interactive documentation** (Swagger UI).

---

## Minikube Testing & Verification

### Manual Feature Testing

Test all **7 Phase 5 Part A features** to verify deployment:

#### Feature 1: Task Priorities

1. **Create task with high priority**:
   - Navigate to http://localhost:3000
   - Click "New Task"
   - Enter title: "Urgent: Deploy to production"
   - Select priority: **High**
   - Click "Create"

2. **Verify priority displayed**:
   - Task should show red badge "High Priority"

3. **Filter by priority**:
   - Click filter dropdown → select "High Priority"
   - Verify only high-priority tasks shown

**Expected Result**: Priority filtering works correctly.

---

#### Feature 2: Task Tags

1. **Create task with tags**:
   - Click "New Task"
   - Enter title: "Review pull request"
   - Add tags: `work`, `code-review`, `urgent`
   - Click "Create"

2. **Verify tags displayed**:
   - Task should show all 3 tags as colored badges

3. **Filter by tag**:
   - Click tag filter → select `work`
   - Verify only tasks with `work` tag shown

**Expected Result**: Tag filtering works correctly.

---

#### Feature 3: Search Tasks

1. **Create multiple tasks**:
   - "Buy groceries"
   - "Prepare presentation"
   - "Call dentist"

2. **Search by keyword**:
   - Enter "presentation" in search bar
   - Press Enter

3. **Verify search results**:
   - Only "Prepare presentation" task shown

**Expected Result**: Search filters tasks correctly.

---

#### Feature 4: Due Dates

1. **Create task with due date**:
   - Click "New Task"
   - Enter title: "Submit report"
   - Click date picker → select date 2 days in future
   - Click "Create"

2. **Verify due date displayed**:
   - Task should show due date with calendar icon

3. **Sort by due date**:
   - Click sort dropdown → select "Due Date"
   - Verify tasks sorted chronologically

**Expected Result**: Due date sorting works correctly.

---

#### Feature 5: Recurring Tasks

1. **Create daily recurring task**:
   - Click "New Task"
   - Enter title: "Daily standup meeting"
   - Enable "Recurring"
   - Select recurrence: **Daily**
   - Click "Create"

2. **Complete the task**:
   - Check the task as complete

3. **Verify next instance auto-created**:
   - Refresh page
   - Verify new task "Daily standup meeting" appears (uncompleted)
   - Verify completed task moved to "Completed" section

**Expected Result**: Next instance auto-created within **5 seconds** via Dapr Pub/Sub event.

**Verification via Kafka**:
```bash
# Check task-events topic for task_completed event
kubectl exec -it todo-kafka-kafka-0 -n kafka -- \
  bin/kafka-console-consumer.sh \
    --bootstrap-server localhost:9092 \
    --topic task-events \
    --from-beginning \
    --max-messages 10
```

You should see JSON event with `event_type: "task_completed"`.

---

#### Feature 6: Reminders

1. **Create task with reminder**:
   - Click "New Task"
   - Enter title: "Team meeting"
   - Set due date: 1 hour in future
   - Enable "Reminder"
   - Set reminder: 15 minutes before due time
   - Click "Create"

2. **Wait for reminder trigger**:
   - Dapr cron binding triggers every 5 minutes
   - Wait up to 5 minutes for next cron cycle

3. **Verify reminder event**:
```bash
# Check reminders topic
kubectl exec -it todo-kafka-kafka-0 -n kafka -- \
  bin/kafka-console-consumer.sh \
    --bootstrap-server localhost:9092 \
    --topic reminders \
    --from-beginning
```

You should see JSON event with task details and reminder time.

**Expected Result**: Reminder event published when due time reached.

---

#### Feature 7: Multi-User Isolation

1. **Create User A account**:
   - Navigate to http://localhost:3000
   - Click "Sign Up"
   - Email: `usera@example.com`
   - Password: `password123`
   - Create task: "User A private task"

2. **Create User B account**:
   - Log out
   - Sign up as `userb@example.com`
   - Create task: "User B private task"

3. **Verify isolation**:
   - Log in as User A
   - Verify User A sees only "User A private task"
   - Verify User A does NOT see "User B private task"

**Expected Result**: Users cannot see each other's tasks (multi-user isolation enforced).

---

### Verification Checklist

Run this checklist to confirm deployment success:

- [ ] All pods Running with 2/2 Ready (application + Dapr sidecar)
- [ ] Frontend accessible at http://localhost:3000
- [ ] Backend API docs accessible at http://localhost:8000/docs
- [ ] User can create task with priority, tags, due date
- [ ] User can filter tasks by priority and tags
- [ ] User can search tasks by keyword
- [ ] User can create recurring task → next instance auto-created on completion
- [ ] Reminder event published to Kafka when due time reached
- [ ] Multi-user isolation verified (User A cannot see User B's tasks)
- [ ] Dapr components healthy: `dapr status -k` shows all True
- [ ] Kafka topics created: `kubectl get kafkatopic -n kafka` shows 3 topics

If all items checked, **Minikube deployment SUCCESSFUL** ✅

---

## Minikube Troubleshooting

### Issue: Pods Not Starting

**Symptom**:
```bash
kubectl get pods
NAME                            READY   STATUS             RESTARTS   AGE
todo-backend-xxxxxxxxxx-xxxxx   0/2     CrashLoopBackOff   3          2m
```

**Diagnosis**:
```bash
# Check pod logs
kubectl logs todo-backend-xxxxxxxxxx-xxxxx -c todo-backend
kubectl logs todo-backend-xxxxxxxxxx-xxxxx -c daprd

# Check pod events
kubectl describe pod todo-backend-xxxxxxxxxx-xxxxx
```

**Common Causes**:

1. **Missing secrets**:
   - Error: `KeyError: 'DATABASE_URL'`
   - Solution: Verify secret created: `kubectl get secret todo-app-secrets`
   - Recreate secret if missing (see Step 1 above)

2. **Database connection failed**:
   - Error: `psycopg2.OperationalError: could not connect to server`
   - Solution: Verify `DATABASE_URL` is correct and Neon database is accessible
   - Test connection: `psql $DATABASE_URL -c "SELECT 1;"`

3. **Dapr sidecar not injected**:
   - Symptom: Pod shows 1/1 Ready instead of 2/2
   - Solution: Verify Dapr annotation in deployment: `kubectl get deployment todo-backend -o yaml | grep dapr.io/enabled`
   - Expected: `dapr.io/enabled: "true"`

4. **Image pull error**:
   - Error: `ErrImagePull` or `ImagePullBackOff`
   - Solution: Verify images exist locally: `docker images | grep todo`
   - Rebuild images: `docker build -f docker/backend.Dockerfile -t todo-backend:latest .`

---

### Issue: Service Unreachable

**Symptom**:
```bash
curl http://localhost:3000
curl: (7) Failed to connect to localhost port 3000: Connection refused
```

**Diagnosis**:
```bash
# Check service exists
kubectl get svc todo-frontend

# Check service endpoints
kubectl get endpoints todo-frontend
```

**Common Causes**:

1. **Port-forward not running**:
   - Solution: Run port-forward in separate terminal: `kubectl port-forward svc/todo-frontend 3000:3000`

2. **Service selector mismatch**:
   - Solution: Verify service selector matches pod labels:
   ```bash
   kubectl get svc todo-frontend -o yaml | grep selector
   kubectl get pods --show-labels
   ```

3. **Pod not ready**:
   - Solution: Wait for pod to reach 2/2 Ready: `kubectl get pods -w`

---

### Issue: Dapr Component Not Loaded

**Symptom**:
```bash
dapr status -k
# One or more components show HEALTHY: False
```

**Diagnosis**:
```bash
# Check Dapr sidecar logs
kubectl logs todo-backend-xxxxxxxxxx-xxxxx -c daprd | grep -i error

# Check component configuration
kubectl get components
kubectl describe component pubsub-kafka
```

**Common Causes**:

1. **Kafka not ready**:
   - Error: `failed to init pubsub.kafka: kafka: client has run out of available brokers`
   - Solution: Verify Kafka cluster ready: `kubectl get kafka todo-kafka -n kafka`
   - Wait for `READY: True`

2. **Database connection failed**:
   - Error: `failed to init state.postgresql`
   - Solution: Verify `DATABASE_URL` in secrets and database accessible

3. **Component YAML invalid**:
   - Solution: Validate component YAML:
   ```bash
   kubectl apply --dry-run=client -f k8s/dapr/components/pubsub-kafka.yaml
   ```

---

### Issue: Kafka Topic Not Created

**Symptom**:
```bash
kubectl get kafkatopic -n kafka
No resources found in kafka namespace.
```

**Diagnosis**:
```bash
# Check Strimzi operator logs
kubectl logs -n kafka deployment/strimzi-cluster-operator

# Check Kafka cluster status
kubectl get kafka todo-kafka -n kafka -o yaml
```

**Common Causes**:

1. **Kafka cluster not ready**:
   - Solution: Wait for cluster: `kubectl wait kafka/todo-kafka --for=condition=Ready --timeout=300s -n kafka`

2. **Topic YAML invalid**:
   - Solution: Validate topic YAML:
   ```bash
   kubectl apply --dry-run=client -f k8s/kafka/kafka-topics.yaml
   ```

3. **Strimzi operator not running**:
   - Solution: Verify operator pod: `kubectl get pods -n kafka`
   - Reinstall if missing: `helm install strimzi strimzi/strimzi-kafka-operator -n kafka`

---

## Minikube Cleanup

To completely remove Todo application and Minikube cluster:

### Remove Todo Application

```bash
# Uninstall Helm release
helm uninstall todo -n default

# Delete secrets
kubectl delete secret todo-app-secrets -n default

# Delete Dapr components
kubectl delete -f k8s/dapr/components/ -n default
```

**Expected Output**:
```
release "todo" uninstalled
secret "todo-app-secrets" deleted
component.dapr.io "pubsub-kafka" deleted
component.dapr.io "statestore-postgresql" deleted
component.dapr.io "binding-cron" deleted
component.dapr.io "secrets-kubernetes" deleted
configuration.dapr.io "dapr-config" deleted
```

---

### Remove Kafka

```bash
# Delete Kafka topics
kubectl delete -f k8s/kafka/kafka-topics.yaml -n kafka

# Delete Kafka cluster
kubectl delete -f k8s/kafka/kafka-cluster.yaml -n kafka

# Uninstall Strimzi operator
helm uninstall strimzi -n kafka

# Delete kafka namespace
kubectl delete namespace kafka
```

**Expected Output**:
```
kafkatopic.kafka.strimzi.io "task-events" deleted
kafkatopic.kafka.strimzi.io "reminders" deleted
kafkatopic.kafka.strimzi.io "task-updates" deleted
kafka.kafka.strimzi.io "todo-kafka" deleted
release "strimzi" uninstalled
namespace "kafka" deleted
```

---

### Remove Dapr

```bash
dapr uninstall -k
```

**Expected Output**:
```
✅  Dapr has been uninstalled successfully
```

---

### Delete Minikube Cluster

```bash
minikube delete
```

**Expected Output**:
```
🔥  Deleting "minikube" in docker ...
🔥  Deleting container "minikube" ...
🔥  Removing /Users/username/.minikube/machines/minikube ...
💀  Removed all traces of the "minikube" cluster.
```

**Disk Space Reclaimed**: ~10-20 GB (Docker images, cluster data, logs)

---

# Part 2: Oracle OKE Cloud Deployment

## Prerequisites (OKE)

### Oracle Cloud Account

**Required**: Oracle Cloud account with **Always Free Tier** eligibility

**Create Account**:
1. Navigate to [Oracle Cloud Free Tier](https://www.oracle.com/cloud/free/)
2. Click "Start for free"
3. Complete registration (requires credit card for verification, but **no charges** for free tier resources)

**Verify Free Tier Eligibility**:
- 4 OCPUs ARM-based Compute (Ampere A1)
- 24 GB RAM
- 200 GB storage
- Always Free (no time limit)

**Tenancy Information**:
After registration, note the following:
- **Tenancy OCID**: Found in Profile → Tenancy
- **User OCID**: Found in Profile → User Settings
- **Region**: Select home region (e.g., `us-phoenix-1`)

---

### OCI CLI Installation

**Version Required**: Latest

```bash
# Verify installation
oci --version
# Expected output: X.XX.X or higher
```

**Installation**:

```bash
# macOS with Homebrew
brew install oci-cli

# Linux (requires Python 3.8+)
bash -c "$(curl -L https://raw.githubusercontent.com/oracle/oci-cli/master/scripts/install/install.sh)"

# Windows (requires Python 3.8+)
# Download installer from https://docs.oracle.com/en-us/iaas/Content/API/SDKDocs/climanualinst.htm
```

**Configuration**:
```bash
oci setup config
```

**Expected Prompts**:
```
Enter a location for your config [C:\Users\username\.oci\config]:
Enter a user OCID: ocid1.user.oc1..aaaaaaaaxxx
Enter a tenancy OCID: ocid1.tenancy.oc1..aaaaaaaaxxx
Enter a region (e.g. us-phoenix-1): us-phoenix-1
Do you want to generate a new API Signing RSA key pair? [Y/n]: Y
Enter a directory for your keys to be created [C:\Users\username\.oci]:
Enter a name for your key [oci_api_key]:
```

**Generate API Key**:
OCI CLI will generate RSA key pair:
- **Private key**: `~/.oci/oci_api_key.pem` (keep secure)
- **Public key**: `~/.oci/oci_api_key_public.pem`

**Upload Public Key to Oracle Cloud**:
1. Navigate to Oracle Cloud Console → Profile → User Settings
2. Click "API Keys" → "Add API Key"
3. Upload `~/.oci/oci_api_key_public.pem`
4. Click "Add"

**Verification**:
```bash
oci iam region list
```

**Expected Output**: List of Oracle Cloud regions (JSON format)

---

### kubectl, Helm, Dapr CLI

Use the same versions as Minikube prerequisites:
- **kubectl**: 1.27+
- **Helm**: 3.12+
- **Dapr CLI**: 1.14+

See [Minikube Prerequisites](#required-tools) for installation instructions.

---

## OKE Cluster Provisioning

**Estimated Time**: 20-30 minutes (cluster creation)

### Option A: Provision via OCI Console (Recommended for First-Time)

#### Step 1: Navigate to OKE

1. Log in to [Oracle Cloud Console](https://cloud.oracle.com/)
2. Click hamburger menu (☰) → **Developer Services** → **Kubernetes Clusters (OKE)**
3. Click **Create cluster**

---

#### Step 2: Configure Cluster

**Cluster Type**: Select **Quick Create**

**Configuration**:
- **Name**: `todo-app-cluster`
- **Compartment**: Select your compartment (or create new)
- **Kubernetes version**: 1.28 or 1.29 (latest stable)
- **Kubernetes API endpoint**: **Public endpoint**
- **Kubernetes worker nodes**: **Public workers**
- **Shape**: **VM.Standard.A1.Flex** (ARM-based, free tier eligible)
  - **OCPUs**: 4
  - **Memory (GB)**: 24
- **Node count**: **1** (free tier limit)
- **Pod CIDR**: 10.244.0.0/16 (default)
- **Service CIDR**: 10.96.0.0/16 (default)

**Networking** (Quick Create auto-configures):
- New VCN created with public/private subnets
- Internet Gateway, NAT Gateway, Service Gateway auto-created

Click **Next** → Review → **Create cluster**

**Expected Output**:
```
Cluster creation initiated. Cluster will be ready in 15-20 minutes.
```

**Monitor Progress**:
- Cluster status: Creating → Active (wait 15-20 minutes)
- Node pool status: Creating → Active

---

#### Step 3: Download kubeconfig

Once cluster status is **Active**:

1. Click cluster name → **Access Cluster**
2. Copy `oci ce cluster create-kubeconfig` command
3. Run in terminal:

```bash
oci ce cluster create-kubeconfig \
  --cluster-id ocid1.cluster.oc1.phx.aaaaaaaaxxxxxx \
  --file $HOME/.kube/config-oke \
  --region us-phoenix-1 \
  --token-version 2.0.0 \
  --kube-endpoint PUBLIC_ENDPOINT
```

**Expected Output**:
```
New config written to the Kubeconfig file C:\Users\username\.kube\config-oke
```

**Set kubectl context**:
```bash
export KUBECONFIG=$HOME/.kube/config-oke
kubectl config use-context context-xxxxxx
```

**Verification**:
```bash
kubectl cluster-info
kubectl get nodes
```

**Expected Output**:
```
Kubernetes control plane is running at https://xxx.xxx.xxx.xxx:6443
CoreDNS is running at https://xxx.xxx.xxx.xxx:6443/api/v1/namespaces/kube-system/services/kube-dns:dns/proxy

NAME           STATUS   ROLES   AGE   VERSION
10.0.10.xxx    Ready    node    5m    v1.28.2
```

**Node should show STATUS: Ready**

---

### Option B: Provision via OCI CLI (Advanced)

For automation and infrastructure-as-code:

```bash
# Set variables
export COMPARTMENT_ID="ocid1.compartment.oc1..aaaaaaaaxxx"
export VCN_ID="ocid1.vcn.oc1.phx.aaaaaaaaxxx"  # Or create new VCN
export SUBNET_ID="ocid1.subnet.oc1.phx.aaaaaaaaxxx"

# Create OKE cluster (simplified)
oci ce cluster create \
  --compartment-id $COMPARTMENT_ID \
  --name todo-app-cluster \
  --kubernetes-version v1.28.2 \
  --vcn-id $VCN_ID \
  --service-lb-subnet-ids '["'$SUBNET_ID'"]' \
  --wait-for-state ACTIVE
```

**Note**: Full OCI CLI provisioning requires VCN, subnets, and security lists pre-configured. **OCI Console Quick Create is recommended for first-time setup.**

---

### Create Namespaces

Create dedicated namespaces for application, Kafka, and monitoring:

```bash
kubectl create namespace todo
kubectl create namespace kafka
kubectl create namespace monitoring
```

**Expected Output**:
```
namespace/todo created
namespace/kafka created
namespace/monitoring created
```

**Verification**:
```bash
kubectl get namespaces
```

**Expected Output**:
```
NAME              STATUS   AGE
default           Active   10m
kube-system       Active   10m
kube-public       Active   10m
kube-node-lease   Active   10m
todo              Active   5s
kafka             Active   5s
monitoring        Active   5s
```

---

## Dapr Installation on OKE

**Estimated Time**: 3-5 minutes

### Step 1: Add Dapr Helm Repository

```bash
helm repo add dapr https://dapr.github.io/helm-charts/
helm repo update
```

**Expected Output**:
```
"dapr" has been added to your repositories
Hang tight while we grab the latest from your chart repositories...
...Successfully got an update from the "dapr" chart repository
Update Complete. ⎈Happy Helming!⎈
```

---

### Step 2: Install Dapr via Helm

```bash
helm install dapr dapr/dapr \
  --namespace dapr-system \
  --create-namespace \
  --set global.ha.enabled=false \
  --wait
```

**Configuration Notes**:
- `global.ha.enabled=false`: Disables high-availability mode (single node cluster)
- `--wait`: Waits for all pods to be ready before returning

**Expected Output**:
```
NAME: dapr
LAST DEPLOYED: Sun Feb  9 11:00:00 2026
NAMESPACE: dapr-system
STATUS: deployed
REVISION: 1
TEST SUITE: None
NOTES:
Thank you for installing Dapr: High-performance, lightweight serverless runtime for cloud and edge

Your release is named dapr.
...
```

**Estimated Time**: 2-3 minutes

---

### Step 3: Verify Dapr Installation

```bash
dapr status -k
```

**Expected Output**:
```
  NAME                   NAMESPACE    HEALTHY  STATUS   REPLICAS  VERSION  AGE  CREATED
  dapr-sidecar-injector  dapr-system  True     Running  1         1.14.0   2m   2026-02-09 11:00.00
  dapr-sentry            dapr-system  True     Running  1         1.14.0   2m   2026-02-09 11:00.00
  dapr-operator          dapr-system  True     Running  1         1.14.0   2m   2026-02-09 11:00.00
  dapr-placement         dapr-system  True     Running  1         1.14.0   2m   2026-02-09 11:00.00
  dapr-dashboard         dapr-system  True     Running  1         1.14.0   2m   2026-02-09 11:00.00
```

**All services should show HEALTHY: True**

---

### Step 4: Deploy Dapr Components

Deploy Dapr components to `todo` namespace:

```bash
kubectl apply -f k8s/dapr/components/ -n todo
```

**Expected Output**:
```
component.dapr.io/pubsub-kafka created
component.dapr.io/statestore-postgresql created
component.dapr.io/binding-cron created
component.dapr.io/secrets-kubernetes created
configuration.dapr.io/dapr-config created
```

**Verification**:
```bash
kubectl get components -n todo
```

**Expected Output**:
```
NAME                     AGE
pubsub-kafka             10s
statestore-postgresql    10s
binding-cron             10s
secrets-kubernetes       10s
```

---

## Kafka Deployment on OKE

**Estimated Time**: 10-15 minutes

### Option A: Self-Hosted Strimzi Kafka (Free, More Control)

#### Step 1: Install Strimzi Operator

```bash
helm repo add strimzi https://strimzi.io/charts/
helm repo update

helm install strimzi strimzi/strimzi-kafka-operator \
  -n kafka \
  --set watchAnyNamespace=true \
  --wait
```

**Expected Output**:
```
NAME: strimzi
LAST DEPLOYED: Sun Feb  9 11:10:00 2026
NAMESPACE: kafka
STATUS: deployed
REVISION: 1
TEST SUITE: None
```

**Verification**:
```bash
kubectl get pods -n kafka
```

**Expected Output**:
```
NAME                                        READY   STATUS    RESTARTS   AGE
strimzi-cluster-operator-xxxxxxxxxx-xxxxx   1/1     Running   0          30s
```

---

#### Step 2: Deploy Kafka Cluster

Deploy minimal Kafka cluster for OKE:

```bash
kubectl apply -f k8s/kafka/kafka-cluster.yaml -n kafka
```

**Wait for cluster to become ready**:
```bash
kubectl wait kafka/todo-kafka --for=condition=Ready --timeout=600s -n kafka
```

**Expected Output**:
```
kafka.kafka.strimzi.io/todo-kafka condition met
```

**Verification**:
```bash
kubectl get kafka -n kafka
```

**Expected Output**:
```
NAME         DESIRED KAFKA REPLICAS   DESIRED ZK REPLICAS   READY   METADATA STATE   WARNINGS
todo-kafka   1                        1                     True    KRaft
```

**Estimated Time**: 5-7 minutes

---

#### Step 3: Create Kafka Topics

```bash
kubectl apply -f k8s/kafka/kafka-topics.yaml -n kafka
```

**Expected Output**:
```
kafkatopic.kafka.strimzi.io/task-events created
kafkatopic.kafka.strimzi.io/reminders created
kafkatopic.kafka.strimzi.io/task-updates created
```

**Verification**:
```bash
kubectl get kafkatopic -n kafka
```

**Expected Output**:
```
NAME           CLUSTER      PARTITIONS   REPLICATION FACTOR   READY
task-events    todo-kafka   3            1                    True
reminders      todo-kafka   1            1                    True
task-updates   todo-kafka   3            1                    True
```

---

### Option B: Managed Redpanda Cloud (Recommended for Production)

**Advantages**:
- Fully managed (no operator overhead)
- Free serverless tier (10 GB storage, 100 MB/s)
- Lower operational complexity
- Better performance on limited resources

#### Step 1: Create Redpanda Cloud Account

1. Navigate to [Redpanda Cloud](https://redpanda.com/try-redpanda)
2. Sign up for **Serverless Free Tier**
3. Create cluster:
   - **Cluster name**: `todo-kafka`
   - **Region**: Same as OKE cluster (e.g., `us-west-2`)
   - **Tier**: Serverless Free

**Wait for cluster creation** (3-5 minutes)

---

#### Step 2: Create Kafka Topics

In Redpanda Console:
1. Navigate to **Topics** → **Create Topic**
2. Create topics:
   - `task-events` (3 partitions, 1 replica)
   - `reminders` (1 partition, 1 replica)
   - `task-updates` (3 partitions, 1 replica)

---

#### Step 3: Get Bootstrap Servers

1. Navigate to **Cluster Settings** → **Bootstrap Servers**
2. Copy bootstrap server URL: `xxx.yyy.cloud.redpanda.com:9092`

---

#### Step 4: Update Dapr Pub/Sub Component

Edit `k8s/dapr/components/pubsub-kafka.yaml`:

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: pubsub-kafka
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    - name: brokers
      value: "xxx.yyy.cloud.redpanda.com:9092"
    - name: authType
      value: "sasl_plain"
    - name: saslUsername
      secretKeyRef:
        name: kafka-secrets
        key: sasl_username
    - name: saslPassword
      secretKeyRef:
        name: kafka-secrets
        key: sasl_password
```

**Create Kafka credentials secret**:
```bash
kubectl create secret generic kafka-secrets \
  --from-literal=sasl_username="your-redpanda-username" \
  --from-literal=sasl_password="your-redpanda-password" \
  -n todo
```

**Apply updated component**:
```bash
kubectl apply -f k8s/dapr/components/pubsub-kafka.yaml -n todo
```

---

## Application Deployment to OKE

**Estimated Time**: 10-15 minutes

### Step 1: Build and Push Docker Images

#### Set Container Registry Variables

```bash
# For GitHub Container Registry (ghcr.io)
export REGISTRY="ghcr.io"
export NAMESPACE="your-github-username"
export TAG="latest"

# For Oracle Container Image Registry (OCIR)
# export REGISTRY="us-phoenix-1.ocir.io"
# export NAMESPACE="your-tenancy-namespace/your-username"
```

---

#### Build Frontend Image

```bash
cd frontend
docker build -f ../docker/frontend.Dockerfile -t $REGISTRY/$NAMESPACE/todo-frontend:$TAG .
docker push $REGISTRY/$NAMESPACE/todo-frontend:$TAG
```

**Expected Output**:
```
[+] Building 180.5s (15/15) FINISHED
...
=> exporting to image
=> pushing layers
=> pushing manifest for ghcr.io/username/todo-frontend:latest
```

**Estimated Time**: 5-8 minutes (depends on network speed)

---

#### Build Backend Image

```bash
cd ../backend
docker build -f ../docker/backend.Dockerfile -t $REGISTRY/$NAMESPACE/todo-backend:$TAG .
docker push $REGISTRY/$NAMESPACE/todo-backend:$TAG
```

**Expected Output**:
```
[+] Building 90.2s (12/12) FINISHED
...
=> pushing manifest for ghcr.io/username/todo-backend:latest
```

**Estimated Time**: 3-5 minutes

---

### Step 2: Create Image Pull Secret (if using private registry)

```bash
kubectl create secret docker-registry regcred \
  --docker-server=$REGISTRY \
  --docker-username=your-username \
  --docker-password=your-password \
  --docker-email=your-email \
  -n todo
```

**For GitHub Container Registry**:
```bash
kubectl create secret docker-registry regcred \
  --docker-server=ghcr.io \
  --docker-username=your-github-username \
  --docker-password=your-github-personal-access-token \
  --docker-email=your-email \
  -n todo
```

**Expected Output**:
```
secret/regcred created
```

---

### Step 3: Create Application Secrets

Create secrets for database, authentication, and API keys:

```bash
kubectl create secret generic todo-app-secrets \
  --from-literal=DATABASE_URL="postgresql://user:password@host.neon.tech/database?sslmode=require" \
  --from-literal=BETTER_AUTH_SECRET="your-32-char-secret" \
  --from-literal=COHERE_API_KEY="your-cohere-api-key" \
  --from-literal=NEXTAUTH_URL="https://your-oke-domain.com" \
  --from-literal=NEXTAUTH_SECRET="your-nextauth-secret" \
  -n todo
```

**Expected Output**:
```
secret/todo-app-secrets created
```

**Verification**:
```bash
kubectl get secret todo-app-secrets -n todo
```

---

### Step 4: Deploy via Helm

Deploy application using OKE-specific values:

```bash
helm install todo ./k8s/helm/todo-app \
  -f ./k8s/helm/todo-app/values-oke.yaml \
  --set image.frontend.repository=$REGISTRY/$NAMESPACE/todo-frontend \
  --set image.frontend.tag=$TAG \
  --set image.backend.repository=$REGISTRY/$NAMESPACE/todo-backend \
  --set image.backend.tag=$TAG \
  -n todo \
  --wait
```

**Expected Output**:
```
NAME: todo
LAST DEPLOYED: Sun Feb  9 12:00:00 2026
NAMESPACE: todo
STATUS: deployed
REVISION: 1
TEST SUITE: None
NOTES:
1. Get the application URL by running these commands:
  export INGRESS_IP=$(kubectl get svc -n ingress-nginx ingress-nginx-controller -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
  echo http://$INGRESS_IP

2. Access the backend API:
  echo http://$INGRESS_IP/api/docs
```

**Estimated Time**: 3-5 minutes

---

### Step 5: Verify Pods Running

```bash
kubectl get pods -n todo -w
```

**Expected Output** (wait until all pods 2/2 Ready):
```
NAME                            READY   STATUS    RESTARTS   AGE
todo-backend-xxxxxxxxxx-xxxxx   2/2     Running   0          2m
todo-backend-xxxxxxxxxx-xxxxx   2/2     Running   0          2m
todo-backend-xxxxxxxxxx-xxxxx   2/2     Running   0          2m
todo-frontend-xxxxxxxxxx-xxxxx  2/2     Running   0          2m
todo-frontend-xxxxxxxxxx-xxxxx  2/2     Running   0          2m
todo-frontend-xxxxxxxxxx-xxxxx  2/2     Running   0          2m
```

**Note**: OKE values-oke.yaml configures **3 replicas** for high availability.

**Timeout**: Pods should be Ready within **5 minutes**.

---

### Step 6: Get Load Balancer IP

Get public IP address for Ingress controller:

```bash
kubectl get svc -n ingress-nginx ingress-nginx-controller
```

**Expected Output**:
```
NAME                       TYPE           CLUSTER-IP      EXTERNAL-IP      PORT(S)                      AGE
ingress-nginx-controller   LoadBalancer   10.96.xxx.xxx   xxx.xxx.xxx.xxx  80:30080/TCP,443:30443/TCP   5m
```

**Copy EXTERNAL-IP** (e.g., `129.146.123.45`)

**Access application**:
```bash
export INGRESS_IP=$(kubectl get svc -n ingress-nginx ingress-nginx-controller -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
echo "Frontend: http://$INGRESS_IP"
echo "Backend API: http://$INGRESS_IP/api/docs"
```

Open browser and navigate to `http://$INGRESS_IP`

You should see the **Todo Application** login page.

---

## TLS & HTTPS Access

**Estimated Time**: 10-15 minutes

### Step 1: Install cert-manager

Install cert-manager for automatic TLS certificate generation:

```bash
helm repo add jetstack https://charts.jetstack.io
helm repo update

helm install cert-manager jetstack/cert-manager \
  --namespace cert-manager \
  --create-namespace \
  --set crds.enabled=true \
  --wait
```

**Expected Output**:
```
NAME: cert-manager
LAST DEPLOYED: Sun Feb  9 12:15:00 2026
NAMESPACE: cert-manager
STATUS: deployed
REVISION: 1
TEST SUITE: None
```

**Verification**:
```bash
kubectl get pods -n cert-manager
```

**Expected Output**:
```
NAME                                       READY   STATUS    RESTARTS   AGE
cert-manager-xxxxxxxxxx-xxxxx              1/1     Running   0          60s
cert-manager-cainjector-xxxxxxxxxx-xxxxx   1/1     Running   0          60s
cert-manager-webhook-xxxxxxxxxx-xxxxx      1/1     Running   0          60s
```

**Estimated Time**: 2-3 minutes

---

### Step 2: Configure DNS

**Option A: Use nip.io (for testing)**

`nip.io` provides wildcard DNS for any IP address.

Example: `129.146.123.45.nip.io` resolves to `129.146.123.45`

**Set hostname**:
```bash
export HOSTNAME="$INGRESS_IP.nip.io"
echo "Application will be accessible at: https://$HOSTNAME"
```

**Option B: Use custom domain (for production)**

1. Purchase domain (e.g., `example.com`)
2. Create DNS A record:
   - **Name**: `todo` (or `@` for root domain)
   - **Type**: A
   - **Value**: `$INGRESS_IP` (LoadBalancer IP)
   - **TTL**: 300

3. Wait for DNS propagation (1-5 minutes):
```bash
nslookup todo.example.com
```

**Set hostname**:
```bash
export HOSTNAME="todo.example.com"
```

---

### Step 3: Create Let's Encrypt ClusterIssuer

Create ClusterIssuer for Let's Encrypt (free TLS certificates):

```bash
cat <<EOF | kubectl apply -f -
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: your-email@example.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
      - http01:
          ingress:
            class: nginx
EOF
```

**Expected Output**:
```
clusterissuer.cert-manager.io/letsencrypt-prod created
```

**For testing** (higher rate limits):
Replace server URL with: `https://acme-staging-v02.api.letsencrypt.org/directory`

---

### Step 4: Update Ingress with TLS

Update Helm values to enable TLS:

```bash
helm upgrade todo ./k8s/helm/todo-app \
  -f ./k8s/helm/todo-app/values-oke.yaml \
  --set ingress.enabled=true \
  --set ingress.hosts[0].host=$HOSTNAME \
  --set ingress.hosts[0].paths[0].path=/ \
  --set ingress.hosts[0].paths[0].pathType=Prefix \
  --set ingress.tls[0].secretName=todo-tls \
  --set ingress.tls[0].hosts[0]=$HOSTNAME \
  --set ingress.annotations."cert-manager\.io/cluster-issuer"=letsencrypt-prod \
  -n todo \
  --wait
```

**Expected Output**:
```
Release "todo" has been upgraded. Happy Helming!
NAME: todo
LAST DEPLOYED: Sun Feb  9 12:20:00 2026
NAMESPACE: todo
STATUS: deployed
REVISION: 2
```

**Estimated Time**: 1-2 minutes

---

### Step 5: Verify Certificate Issued

Wait for certificate to be issued (1-2 minutes):

```bash
kubectl get certificate -n todo -w
```

**Expected Output**:
```
NAME       READY   SECRET     AGE
todo-tls   False   todo-tls   10s
todo-tls   True    todo-tls   90s
```

**Certificate should show READY: True**

**Check certificate details**:
```bash
kubectl describe certificate todo-tls -n todo
```

**Expected Output** (excerpt):
```
Status:
  Conditions:
    Type:    Ready
    Status:  True
  Not After:  2026-05-10T12:20:00Z
  Not Before: 2026-02-09T12:20:00Z
Events:
  Type    Reason     Age   From                                       Message
  ----    ------     ----  ----                                       -------
  Normal  Issuing    2m    cert-manager-certificates-trigger          Issuing certificate as Secret does not exist
  Normal  Generated  2m    cert-manager-certificates-key-manager      Stored new private key in temporary Secret resource "todo-tls-xxxxx"
  Normal  Requested  2m    cert-manager-certificates-request-manager  Created new CertificateRequest resource "todo-tls-xxxxx"
  Normal  Issuing    90s   cert-manager-certificates-issuing          The certificate has been successfully issued
```

---

### Step 6: Access via HTTPS

Access application via HTTPS:

```bash
echo "Application URL: https://$HOSTNAME"
```

Open browser and navigate to `https://$HOSTNAME`

**Expected Result**:
- ✅ Valid TLS certificate (green padlock in browser)
- ✅ Todo Application login page loads

**Verify certificate**:
- Click padlock icon → Certificate
- **Issued by**: Let's Encrypt
- **Expires**: 90 days from issuance

---

## Production Considerations

### Database: Use Neon PostgreSQL (Externally Hosted)

**Recommended**: Use [Neon](https://neon.tech) managed PostgreSQL (free tier: 3 projects, 10 branches, 5 GB storage)

**Configuration**:
1. Create Neon project
2. Copy connection string: `postgresql://user:password@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require`
3. Update secret:
```bash
kubectl create secret generic todo-app-secrets \
  --from-literal=DATABASE_URL="postgresql://user:password@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require" \
  --dry-run=client -o yaml | kubectl apply -n todo -f -
```

**Advantages**:
- No database pod in OKE cluster (saves resources)
- Automatic backups and point-in-time recovery
- Serverless scaling (auto-pause when idle)
- Free tier sufficient for development/testing

---

### Secrets Management: Use Oracle Vault or external-secrets Operator

**Option A: Oracle Vault (Recommended for Production)**

Oracle Vault provides centralized secret management with audit logging.

1. **Create Vault**:
   - OCI Console → Security → Vault
   - Create Vault: `todo-app-vault`
   - Create Master Encryption Key

2. **Store Secrets in Vault**:
   - Create secrets: `DATABASE_URL`, `BETTER_AUTH_SECRET`, `COHERE_API_KEY`

3. **Install external-secrets Operator**:
```bash
helm repo add external-secrets https://charts.external-secrets.io
helm install external-secrets external-secrets/external-secrets -n external-secrets-system --create-namespace
```

4. **Create SecretStore**:
```yaml
apiVersion: external-secrets.io/v1beta1
kind: SecretStore
metadata:
  name: oracle-vault
  namespace: todo
spec:
  provider:
    oracle:
      vault: ocid1.vault.oc1.phx.aaaaaaaaxxx
      region: us-phoenix-1
      auth:
        tenancy: ocid1.tenancy.oc1..aaaaaaaaxxx
        user: ocid1.user.oc1..aaaaaaaaxxx
        key: /path/to/oci_api_key.pem
        fingerprint: xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx
```

5. **Create ExternalSecret**:
```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: todo-app-secrets
  namespace: todo
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: oracle-vault
    kind: SecretStore
  target:
    name: todo-app-secrets
  data:
    - secretKey: DATABASE_URL
      remoteRef:
        key: database-url
    - secretKey: BETTER_AUTH_SECRET
      remoteRef:
        key: better-auth-secret
```

**Advantages**:
- Centralized secret management
- Automatic secret rotation
- Audit logging
- No secrets in Git or kubectl commands

---

### Monitoring: Deploy Prometheus/Grafana (Phase 8)

**Comprehensive monitoring stack** will be deployed in Phase 8 (User Story 6):

- **Prometheus**: Metrics collection (request rate, latency, error rate, Kafka lag)
- **Grafana**: Dashboards and visualizations
- **Loki**: Log aggregation and search
- **AlertManager**: Alerting and notifications

**Preview**:
```bash
# Install kube-prometheus-stack (Phase 8)
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install kube-prometheus prometheus-community/kube-prometheus-stack -n monitoring
```

See `tasks.md` Phase 8 (T162-T193) for full monitoring implementation.

---

### Backups: Configure OKE Backups and PV Snapshots

**Database Backups**:
- Neon PostgreSQL: Automatic backups (point-in-time recovery up to 7 days on free tier)

**Kubernetes Backups**:
1. **etcd Snapshots** (OKE managed automatically):
   - OKE takes daily etcd snapshots
   - Retention: 30 days

2. **Persistent Volume Snapshots**:
   - If using OCI Block Volumes for Kafka persistent storage:
   ```bash
   # Create VolumeSnapshot
   kubectl apply -f - <<EOF
   apiVersion: snapshot.storage.k8s.io/v1
   kind: VolumeSnapshot
   metadata:
     name: kafka-data-snapshot
     namespace: kafka
   spec:
     volumeSnapshotClassName: oci-bv
     source:
       persistentVolumeClaimName: data-todo-kafka-kafka-0
   EOF
   ```

3. **Application State Backup**:
   - Backup Kubernetes manifests to Git (already done via Helm charts)
   - Backup Dapr state (PostgreSQL) via Neon backups

**Recovery**:
- **Database**: Restore from Neon point-in-time recovery
- **Kubernetes**: Restore from etcd snapshot or redeploy via Helm
- **Persistent Volumes**: Restore from OCI Block Volume snapshots

---

## OKE Troubleshooting

### Issue: Pods Stuck in Pending

**Symptom**:
```bash
kubectl get pods -n todo
NAME                            READY   STATUS    RESTARTS   AGE
todo-backend-xxxxxxxxxx-xxxxx   0/2     Pending   0          5m
```

**Diagnosis**:
```bash
kubectl describe pod todo-backend-xxxxxxxxxx-xxxxx -n todo
```

**Common Causes**:

1. **Insufficient resources**:
   - Error: `0/1 nodes are available: 1 Insufficient cpu`
   - Solution: Check node resources:
   ```bash
   kubectl describe node
   kubectl top node
   ```
   - If resources exhausted, reduce replica count in `values-oke.yaml`:
   ```yaml
   replicaCount: 1  # Reduce from 3 to 1
   ```
   - Redeploy: `helm upgrade todo ./k8s/helm/todo-app -f values-oke.yaml -n todo`

2. **Image pull error**:
   - Error: `Failed to pull image "ghcr.io/username/todo-backend:latest": rpc error: code = Unknown desc = Error response from daemon: pull access denied`
   - Solution: Verify image pull secret:
   ```bash
   kubectl get secret regcred -n todo
   ```
   - Recreate if missing (see Step 2 above)

3. **PersistentVolumeClaim pending**:
   - Error: `pod has unbound immediate PersistentVolumeClaims`
   - Solution: Check PVC:
   ```bash
   kubectl get pvc -n todo
   ```
   - Verify StorageClass exists:
   ```bash
   kubectl get storageclass
   ```

---

### Issue: LoadBalancer External IP Pending

**Symptom**:
```bash
kubectl get svc -n ingress-nginx
NAME                       TYPE           CLUSTER-IP      EXTERNAL-IP   PORT(S)
ingress-nginx-controller   LoadBalancer   10.96.xxx.xxx   <pending>     80:30080/TCP,443:30443/TCP
```

**Diagnosis**:
```bash
kubectl describe svc ingress-nginx-controller -n ingress-nginx
```

**Common Causes**:

1. **OCI Load Balancer quota exceeded**:
   - Error: `Error creating load balancer: Service limit exceeded`
   - Solution: Check OCI tenancy limits:
   ```bash
   oci limits value list --compartment-id $COMPARTMENT_ID --service-name lb
   ```
   - Request limit increase: OCI Console → Governance → Limits, Quotas and Usage

2. **Security list missing ingress rules**:
   - Solution: Verify security lists allow traffic on ports 80/443:
     - OCI Console → Networking → Virtual Cloud Networks → Security Lists
     - Add ingress rule: Source `0.0.0.0/0`, Destination Port `80,443`, Protocol `TCP`

3. **Subnet misconfiguration**:
   - Error: `InvalidSubnet`
   - Solution: Verify subnet is **public** and has **Internet Gateway** route:
     - OCI Console → Networking → Virtual Cloud Networks → Subnets
     - Route Table should have route: Destination `0.0.0.0/0`, Target `Internet Gateway`

**Wait Time**: LoadBalancer provisioning can take **5-10 minutes**. If still pending after 15 minutes, check events:
```bash
kubectl get events -n ingress-nginx --sort-by='.lastTimestamp'
```

---

### Issue: Certificate Not Issued

**Symptom**:
```bash
kubectl get certificate -n todo
NAME       READY   SECRET     AGE
todo-tls   False   todo-tls   10m
```

**Diagnosis**:
```bash
kubectl describe certificate todo-tls -n todo
kubectl describe certificaterequest -n todo
```

**Common Causes**:

1. **DNS not resolving**:
   - Error: `Waiting for HTTP-01 challenge propagation: could not find the start of authority`
   - Solution: Verify DNS resolves to Ingress IP:
   ```bash
   nslookup $HOSTNAME
   dig $HOSTNAME
   ```
   - If using custom domain, wait for DNS propagation (up to 48 hours, usually 1-5 minutes)

2. **Ingress HTTP-01 challenge failed**:
   - Error: `Self check failed for domain: 403`
   - Solution: Verify Ingress controller allows `/.well-known/acme-challenge/` path:
   ```bash
   curl -v http://$HOSTNAME/.well-known/acme-challenge/test
   ```
   - Expected: 404 (not 403 Forbidden)

3. **Let's Encrypt rate limit exceeded**:
   - Error: `too many certificates already issued`
   - Solution: Use Let's Encrypt **staging** server for testing:
   ```yaml
   server: https://acme-staging-v02.api.letsencrypt.org/directory
   ```
   - Rate limits:
     - **Production**: 50 certificates per domain per week
     - **Staging**: Much higher limits (for testing)

4. **cert-manager webhook not ready**:
   - Solution: Verify cert-manager pods running:
   ```bash
   kubectl get pods -n cert-manager
   ```
   - Restart if needed:
   ```bash
   kubectl rollout restart deployment cert-manager -n cert-manager
   kubectl rollout restart deployment cert-manager-webhook -n cert-manager
   ```

---

### Issue: Application Not Accessible via Ingress

**Symptom**:
```bash
curl http://$INGRESS_IP
<html>
<head><title>404 Not Found</title></head>
<body>
<center><h1>404 Not Found</h1></center>
<hr><center>nginx</center>
</body>
</html>
```

**Diagnosis**:
```bash
kubectl get ingress -n todo
kubectl describe ingress todo-ingress -n todo
```

**Common Causes**:

1. **Ingress rules misconfigured**:
   - Solution: Verify Ingress rules match service name and port:
   ```bash
   kubectl get ingress todo-ingress -n todo -o yaml
   ```
   - Check `spec.rules[].http.paths[].backend.service.name` matches: `todo-frontend`
   - Check `spec.rules[].http.paths[].backend.service.port.number` matches: `3000`

2. **Service selector mismatch**:
   - Solution: Verify service selector matches pod labels:
   ```bash
   kubectl get svc todo-frontend -n todo -o yaml | grep selector
   kubectl get pods -n todo --show-labels
   ```
   - Selector should include `app: todo-frontend`

3. **Ingress controller not installed**:
   - Solution: Install ingress-nginx controller:
   ```bash
   helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
   helm install ingress-nginx ingress-nginx/ingress-nginx -n ingress-nginx --create-namespace
   ```

4. **Backend pod not ready**:
   - Solution: Wait for pods to reach 2/2 Ready:
   ```bash
   kubectl get pods -n todo -w
   ```

---

## OKE Cleanup

To completely remove Todo application and OKE cluster:

### Remove Todo Application

```bash
# Uninstall Helm release
helm uninstall todo -n todo

# Delete secrets
kubectl delete secret todo-app-secrets -n todo
kubectl delete secret regcred -n todo

# Delete Dapr components
kubectl delete -f k8s/dapr/components/ -n todo

# Delete namespace
kubectl delete namespace todo
```

**Expected Output**:
```
release "todo" uninstalled
secret "todo-app-secrets" deleted
secret "regcred" deleted
component.dapr.io "pubsub-kafka" deleted
component.dapr.io "statestore-postgresql" deleted
component.dapr.io "binding-cron" deleted
component.dapr.io "secrets-kubernetes" deleted
configuration.dapr.io "dapr-config" deleted
namespace "todo" deleted
```

---

### Remove Kafka (if self-hosted Strimzi)

```bash
# Delete Kafka topics
kubectl delete -f k8s/kafka/kafka-topics.yaml -n kafka

# Delete Kafka cluster
kubectl delete -f k8s/kafka/kafka-cluster.yaml -n kafka

# Uninstall Strimzi operator
helm uninstall strimzi -n kafka

# Delete namespace
kubectl delete namespace kafka
```

**Expected Output**:
```
kafkatopic.kafka.strimzi.io "task-events" deleted
kafkatopic.kafka.strimzi.io "reminders" deleted
kafkatopic.kafka.strimzi.io "task-updates" deleted
kafka.kafka.strimzi.io "todo-kafka" deleted
release "strimzi" uninstalled
namespace "kafka" deleted
```

---

### Remove Dapr

```bash
helm uninstall dapr -n dapr-system
kubectl delete namespace dapr-system
```

**Expected Output**:
```
release "dapr" uninstalled
namespace "dapr-system" deleted
```

---

### Remove cert-manager

```bash
helm uninstall cert-manager -n cert-manager
kubectl delete namespace cert-manager
```

**Expected Output**:
```
release "cert-manager" uninstalled
namespace "cert-manager" deleted
```

---

### Delete OKE Cluster

**Via OCI Console**:
1. Navigate to OKE → Clusters
2. Select `todo-app-cluster`
3. Click **Delete**
4. Confirm deletion (type cluster name)
5. Wait for deletion to complete (5-10 minutes)

**Via OCI CLI**:
```bash
# Get cluster OCID
oci ce cluster list --compartment-id $COMPARTMENT_ID

# Delete cluster
oci ce cluster delete --cluster-id ocid1.cluster.oc1.phx.aaaaaaaaxxx --force
```

**Expected Output**:
```
Are you sure you want to delete this resource? [y/N]: y
{
  "opc-work-request-id": "ocid1.clustersworkrequest.oc1.phx.aaaaaaaaxxx"
}
```

**Verify deletion**:
```bash
oci ce cluster get --cluster-id ocid1.cluster.oc1.phx.aaaaaaaaxxx
```

**Expected Output** (after 5-10 minutes):
```
ServiceError:
{
    "code": "NotAuthorizedOrNotFound",
    "message": "Resource not found or not authorized to access"
}
```

**Cleanup Associated Resources**:
- **Load Balancers**: Automatically deleted with cluster
- **VCN**: Delete manually if created separately (OCI Console → Networking → Virtual Cloud Networks → Delete)
- **Block Volumes**: Delete manually if persistent volumes created (OCI Console → Block Storage → Block Volumes → Terminate)

**Cost Savings**: Deleting cluster and resources **immediately stops all charges** (free tier resources don't incur charges anyway).

---

# Appendices

## Architecture Overview

### System Architecture Diagram (ASCII)

```
┌─────────────────────────────────────────────────────────────────────┐
│                           User Browser                              │
│                         (HTTPS via Ingress)                         │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      Kubernetes Cluster (OKE/Minikube)              │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    Ingress Controller                         │  │
│  │                   (nginx + cert-manager)                      │  │
│  └──────────────────────┬──────────────────┬────────────────────┘  │
│                         │                   │                       │
│         ┌───────────────┴────┐     ┌───────┴───────────┐           │
│         ▼                    ▼     ▼                   ▼           │
│  ┌─────────────┐      ┌─────────────────┐      ┌─────────────┐    │
│  │  Frontend   │      │     Backend      │      │  Dapr       │    │
│  │  (Next.js)  │      │    (FastAPI)     │      │  Dashboard  │    │
│  │  + daprd    │◄────►│    + daprd       │      │             │    │
│  └─────────────┘      └─────────────────┘      └─────────────┘    │
│         │                      │                                    │
│         │                      ▼                                    │
│         │            ┌─────────────────────┐                        │
│         │            │  Dapr Components    │                        │
│         │            │  - Pub/Sub (Kafka)  │                        │
│         │            │  - State (Postgres) │                        │
│         │            │  - Bindings (Cron)  │                        │
│         │            │  - Secrets (K8s)    │                        │
│         │            └──────────┬──────────┘                        │
│         │                       │                                   │
│         └───────────────────────┼───────────────────────────┐       │
│                                 │                           │       │
└─────────────────────────────────┼───────────────────────────┼───────┘
                                  │                           │
                    ┌─────────────┴────────┐     ┌───────────┴────────┐
                    ▼                      ▼     ▼                    ▼
         ┌──────────────────┐   ┌──────────────────────┐   ┌──────────────┐
         │  Kafka Cluster   │   │  Neon PostgreSQL     │   │  Monitoring  │
         │  (Strimzi/       │   │  (External SaaS)     │   │  (Prometheus │
         │   Redpanda)      │   │                      │   │   Grafana)   │
         │                  │   │  - Tasks             │   │              │
         │  - task-events   │   │  - Users             │   │              │
         │  - reminders     │   │  - Conversations     │   │              │
         │  - task-updates  │   │  - Notifications     │   │              │
         │                  │   │  - Audit Logs        │   │              │
         └──────────────────┘   └──────────────────────┘   └──────────────┘
```

### Event Flow Diagram

```
User Action (Complete Task)
    │
    ▼
Frontend (Next.js)
    │ HTTP POST /api/tasks/{id}/complete
    ▼
Backend (FastAPI) + Dapr Sidecar
    │
    ├─► Update task status in PostgreSQL (via Dapr State)
    │
    ├─► Publish "task_completed" event to Kafka (via Dapr Pub/Sub)
    │   │
    │   └─► Kafka Topic: task-events
    │       │
    │       ├─► Audit Service consumes event
    │       │   └─► Creates audit log record
    │       │
    │       └─► Recurring Task Service consumes event
    │           └─► If recurring, creates next instance
    │
    └─► If due_date and reminder_offset configured:
        └─► Dapr Cron Binding triggers at reminder time
            └─► Publishes "reminder" event to Kafka
                │
                └─► Kafka Topic: reminders
                    │
                    └─► Notification Service consumes event
                        └─► Creates notification record
                            │
                            └─► Frontend polls /api/reminders
                                └─► Displays notification to user
```

---

## CLI Reference

### Minikube Commands

| Command | Description |
|---------|-------------|
| `minikube start --cpus=4 --memory=8192` | Start cluster with 4 CPUs, 8 GB RAM |
| `minikube status` | Check cluster status |
| `minikube stop` | Stop cluster (preserves state) |
| `minikube delete` | Delete cluster completely |
| `minikube ip` | Get cluster IP address |
| `minikube service <name>` | Get service URL |
| `minikube addons list` | List available addons |
| `minikube addons enable <addon>` | Enable addon (e.g., ingress) |
| `minikube dashboard` | Open Kubernetes dashboard |
| `minikube logs` | View cluster logs |

---

### kubectl Commands

| Command | Description |
|---------|-------------|
| `kubectl get pods -n <namespace>` | List pods in namespace |
| `kubectl describe pod <pod-name> -n <namespace>` | Describe pod details |
| `kubectl logs <pod-name> -c <container> -n <namespace>` | View container logs |
| `kubectl logs <pod-name> -c <container> -f` | Follow logs (tail) |
| `kubectl exec -it <pod-name> -n <namespace> -- /bin/sh` | Execute shell in pod |
| `kubectl port-forward svc/<service> <local-port>:<remote-port>` | Forward service port |
| `kubectl get svc -n <namespace>` | List services |
| `kubectl get ingress -n <namespace>` | List ingress resources |
| `kubectl get events -n <namespace> --sort-by='.lastTimestamp'` | View recent events |
| `kubectl top node` | View node resource usage |
| `kubectl top pod -n <namespace>` | View pod resource usage |

---

### Helm Commands

| Command | Description |
|---------|-------------|
| `helm repo add <name> <url>` | Add Helm repository |
| `helm repo update` | Update repository indexes |
| `helm search repo <keyword>` | Search charts in repositories |
| `helm install <release> <chart> -n <namespace>` | Install chart as release |
| `helm upgrade <release> <chart> -n <namespace>` | Upgrade existing release |
| `helm uninstall <release> -n <namespace>` | Uninstall release |
| `helm list -n <namespace>` | List installed releases |
| `helm status <release> -n <namespace>` | Show release status |
| `helm get values <release> -n <namespace>` | Show values used for release |
| `helm rollback <release> <revision> -n <namespace>` | Rollback to previous version |

---

### Dapr Commands

| Command | Description |
|---------|-------------|
| `dapr init -k` | Install Dapr on Kubernetes |
| `dapr status -k` | Check Dapr status on Kubernetes |
| `dapr uninstall -k` | Uninstall Dapr from Kubernetes |
| `dapr dashboard -k` | Open Dapr dashboard |
| `dapr invoke -a <app-id> -m <method>` | Invoke Dapr service |
| `dapr publish -p <pubsub> -t <topic> -d <data>` | Publish event to topic |

---

### OCI CLI Commands

| Command | Description |
|---------|-------------|
| `oci ce cluster list --compartment-id <id>` | List OKE clusters |
| `oci ce cluster create-kubeconfig --cluster-id <id>` | Download kubeconfig |
| `oci ce node-pool list --cluster-id <id>` | List node pools |
| `oci compute instance list --compartment-id <id>` | List compute instances |
| `oci lb load-balancer list --compartment-id <id>` | List load balancers |
| `oci iam region list` | List available regions |

---

## Common Errors & Solutions

### Error: `error: You must be logged in to the server (Unauthorized)`

**Cause**: kubectl context not set or kubeconfig expired

**Solution**:
```bash
# For Minikube
kubectl config use-context minikube

# For OKE (regenerate kubeconfig)
oci ce cluster create-kubeconfig --cluster-id <cluster-id> --file ~/.kube/config-oke
export KUBECONFIG=~/.kube/config-oke
```

---

### Error: `ErrImagePull` or `ImagePullBackOff`

**Cause**: Image not found or authentication failed

**Solution**:
```bash
# Verify image exists
docker images | grep todo

# For private registry, create image pull secret
kubectl create secret docker-registry regcred \
  --docker-server=<registry> \
  --docker-username=<username> \
  --docker-password=<password> \
  -n <namespace>

# Update deployment to use image pull secret
# (already configured in Helm chart values-oke.yaml)
```

---

### Error: `CrashLoopBackOff`

**Cause**: Application crashes on startup

**Solution**:
```bash
# Check logs for error messages
kubectl logs <pod-name> -c <container> -n <namespace>

# Common causes:
# 1. Missing environment variables/secrets
# 2. Database connection failed
# 3. Port already in use
# 4. Missing dependencies

# Describe pod for events
kubectl describe pod <pod-name> -n <namespace>
```

---

### Error: `0/1 nodes are available: 1 Insufficient memory`

**Cause**: Insufficient cluster resources

**Solution**:
```bash
# Check node resources
kubectl top node

# Reduce replica count in values file
# values-minikube.yaml or values-oke.yaml
replicaCount: 1  # Reduce from 3

# Redeploy
helm upgrade todo ./k8s/helm/todo-app -f values-minikube.yaml -n default
```

---

### Error: `failed to init pubsub.kafka: kafka: client has run out of available brokers`

**Cause**: Kafka cluster not ready or broker address incorrect

**Solution**:
```bash
# Check Kafka cluster status
kubectl get kafka -n kafka

# Wait for cluster to be Ready
kubectl wait kafka/todo-kafka --for=condition=Ready --timeout=300s -n kafka

# Verify Dapr component has correct broker address
kubectl get component pubsub-kafka -n <namespace> -o yaml

# Expected metadata:
# - name: brokers
#   value: "todo-kafka-kafka-bootstrap.kafka.svc.cluster.local:9092"
```

---

## Performance Tuning

### Optimize Minikube Resources

**Insufficient Resources**:
```bash
# Stop Minikube
minikube stop

# Delete cluster
minikube delete

# Restart with more resources
minikube start --cpus=6 --memory=12288 --disk-size=100g
```

**Recommended for Phase 5**:
- **CPUs**: 6 (Dapr + Kafka + app pods)
- **RAM**: 12 GB (Kafka is memory-intensive)
- **Disk**: 100 GB (Kafka logs, Docker images, Prometheus metrics)

---

### Optimize OKE Node Pool

**Scale Node Pool**:
```bash
# Via OCI Console
# OKE → Clusters → Node Pools → Edit → Increase node count to 2-3

# Via OCI CLI
oci ce node-pool update \
  --node-pool-id <node-pool-id> \
  --size 2
```

**Recommended for Production**:
- **Nodes**: 2-3 (high availability)
- **Shape**: VM.Standard.E4.Flex (Intel, better compatibility) or VM.Standard.A1.Flex (ARM, free tier)
- **OCPUs per node**: 2-4
- **Memory per node**: 16-32 GB

---

### Optimize Kafka Performance

**Increase Partitions**:
```yaml
# k8s/kafka/kafka-topics.yaml
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: task-events
spec:
  partitions: 6  # Increase from 3
  replicas: 1
```

**Tune Consumer Groups**:
```yaml
# Dapr Pub/Sub component metadata
- name: consumerGroup
  value: "task-events-consumer"
- name: maxMessageBytes
  value: "1048576"  # 1 MB
- name: sessionTimeout
  value: "30000"  # 30 seconds
```

---

### Optimize PostgreSQL Connections

**Connection Pooling**:
```python
# backend/app/core/database.py
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,  # Max 10 connections per pod
    max_overflow=5,  # Allow 5 extra connections during spikes
    pool_timeout=30,  # Wait 30s for connection
    pool_recycle=3600,  # Recycle connections every hour
)
```

**Neon Connection Limits** (free tier):
- **Max connections**: 100
- **Recommended**: 10 connections per backend pod × 3 replicas = 30 total

---

## Next Steps

After completing this quickstart:

1. **Implement User Story 2** (Reminders): Tasks T071-T090 in `tasks.md`
2. **Implement User Story 3** (Audit Logging): Tasks T091-T110 in `tasks.md`
3. **Implement User Story 5** (CI/CD Pipeline): Tasks T146-T161 in `tasks.md`
4. **Implement User Story 6** (Monitoring & Observability): Tasks T162-T193 in `tasks.md`

---

## Support & Resources

**Documentation**:
- [Dapr Documentation](https://docs.dapr.io/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Helm Documentation](https://helm.sh/docs/)
- [Oracle OKE Documentation](https://docs.oracle.com/en-us/iaas/Content/ContEng/home.htm)
- [Strimzi Kafka Operator](https://strimzi.io/docs/)
- [cert-manager Documentation](https://cert-manager.io/docs/)

**Troubleshooting**:
- Dapr GitHub Issues: https://github.com/dapr/dapr/issues
- Kubernetes Community Forums: https://discuss.kubernetes.io/
- OKE Community: https://cloudcustomerconnect.oracle.com/

**Contact**:
- Project Repository: [Your GitHub Repository URL]
- Issues: [Your GitHub Issues URL]

---

**End of Quickstart Guide**

**Document Version**: 1.0
**Last Updated**: 2026-02-09
**Total Pages**: ~90 (estimated printed pages)
**Total Lines**: ~1500 lines
