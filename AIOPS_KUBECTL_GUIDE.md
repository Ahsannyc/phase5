# Phase 5: AIOps with kubectl-ai & kagent Guide

**Phase**: 5 (Cloud-Native Deployment - AI Operations)
**Tasks**: T060-T074 (kubectl-ai prompts, kagent analysis, chat integration)
**Duration**: ~1.5 hours (setup and example execution)

## Overview

This guide documents AI-powered Kubernetes operations (AIOps) using:
- ✅ **kubectl-ai**: Natural language Kubernetes commands
- ✅ **kagent**: Cluster analysis and insights
- ✅ **Chat API integration**: AI-driven task management and cluster operations
- ✅ **LLM-based troubleshooting**: Automated problem diagnosis

These tools enable operators to manage Kubernetes clusters using conversational AI instead of memorizing complex kubectl syntax.

**Prerequisites**: Kubernetes cluster running (Minikube or cloud), kubectl configured, Python 3.8+

---

## Part 1: kubectl-ai Setup & Usage

### Installation

```bash
# Install kubectl-ai via pip
pip install kubectl-ai

# Verify installation
kubectl-ai --version

# Set API key (uses default LLM provider)
export OPENAI_API_KEY="sk-your-key-here"  # or COHERE_API_KEY

# Or configure default provider in ~/.kube/kubectl-ai.yaml:
# provider: openai  # or "cohere"
# model: gpt-4      # or "command-r-plus"
# temperature: 0.7
```

### Basic Usage Pattern

```bash
# Standard kubectl-ai syntax:
kubectl-ai "<natural-language-request>"

# The AI generates and executes the kubectl command
# For approval-only mode:
kubectl-ai --dry-run "<natural-language-request>"
```

---

## Phase 5 AIOps Tasks (T060-T074)

### Section 1: Deployment & Pod Management (T060-T065)

#### T060: Scale Deployment via Natural Language

```bash
# Request: Scale backend to 3 replicas
kubectl-ai "scale the backend deployment to 3 replicas"

# Generated command (AI-inferred):
# kubectl scale deployment todo-app-backend --replicas=3

# Expected output:
# deployment.apps/todo-app-backend scaled

# Verify scaling
kubectl get deployment todo-app-backend -w

# Expected: Replicas field changes from 1 to 3
# NAME                   READY   UP-TO-DATE   AVAILABLE   AGE
# todo-app-backend       3/3     3            3           2m

# Monitor pod startup
kubectl get pods -l app=todo-app-backend -w
```

**Pass Criteria**:
- ✅ Natural language interpreted correctly
- ✅ Deployment scaled to requested replica count
- ✅ New pods start automatically
- ✅ Existing connections continue without disruption

#### T061: Get Pod Logs via Natural Language

```bash
# Request: Show recent error logs from backend
kubectl-ai "show me the error logs from the backend pod"

# Generated command (AI-inferred):
# kubectl logs -l app=todo-app-backend --tail=50 --grep=ERROR

# Or more specifically:
kubectl-ai "show backend pod logs from last 10 minutes"

# Generated:
# kubectl logs -l app=todo-app-backend --tail=100 --since=10m

# Expected output: Recent application logs

# With timestamps and context:
kubectl logs -f -l app=todo-app-backend --timestamps=true

# View all containers (if pod has multiple)
kubectl logs <pod-name> --all-containers=true

# Stream logs in real-time
kubectl logs -f deployment/todo-app-backend
```

**Pass Criteria**:
- ✅ Pod/deployment identified from natural language
- ✅ Appropriate kubectl logs command generated
- ✅ Logs returned with context
- ✅ Filtering/sorting options respected

#### T062: Restart Pod via Natural Language

```bash
# Request: Restart the backend pods
kubectl-ai "restart the backend pods"

# Generated command (AI infers rolling restart):
# kubectl rollout restart deployment/todo-app-backend

# Expected output:
# deployment.apps/todo-app-backend restarted

# Verify rollout status
kubectl rollout status deployment/todo-app-backend -w

# Expected: All pods restart and return to Running state
# Waiting for deployment "todo-app-backend" rollout to finish: 1 old replicas pending termination...
# Waiting for deployment "todo-app-backend" rollout to finish: 1 old replicas pending termination...
# Waiting for deployment "todo-app-backend" rollout to finish: 0 old replicas pending termination
# deployment "todo-app-backend" successfully rolled out

# Alternative: Delete specific pod to force restart
kubectl-ai "delete the first backend pod"

# Generated:
# kubectl delete pod todo-app-backend-xxxxx

# Expected: Pod terminated and respawned by deployment controller
```

**Pass Criteria**:
- ✅ Pods identified and restarted correctly
- ✅ No downtime (rolling restart)
- ✅ Rollout completes successfully
- ✅ Services remain healthy during restart

#### T063: Port Forward via Natural Language

```bash
# Request: Forward backend port locally
kubectl-ai "forward port 8000 from the backend to localhost"

# Generated command:
# kubectl port-forward svc/todo-app-backend 8000:8000

# Expected output:
# Forwarding from 127.0.0.1:8000 -> 8000
# Forwarding from [::1]:8000 -> 8000

# In another terminal, test:
curl http://localhost:8000/health

# Expected:
# {"status":"healthy"}

# Stop port-forward (Ctrl+C in original terminal)

# For frontend access:
kubectl-ai "forward frontend port 3000"

# Generated:
# kubectl port-forward svc/todo-app-frontend 3000:3000

# Access in browser: http://localhost:3000
```

**Pass Criteria**:
- ✅ Port forward established correctly
- ✅ Service identified and mapped
- ✅ Port accessible from local machine
- ✅ Can reach pods/services via forwarded port

#### T064: Describe Pod Status via Natural Language

```bash
# Request: What's wrong with the backend pod?
kubectl-ai "why is the backend pod not ready?"

# AI will:
# 1. Get pod status
# 2. Analyze events/logs
# 3. Provide diagnostic summary

# Possible response:
# "The backend pod is experiencing ImagePullBackOff.
#  The image 'todo-backend:v2.0' does not exist.
#  Please verify the image has been pushed to the registry."

# Verify with kubectl:
kubectl describe pod <backend-pod-name>

# Look for events section showing:
# Type     Reason                 Message
# ----     ------                 -------
# Warning  ImagePullBackOff       Error response from daemon

# Check deployment spec for wrong image:
kubectl get deployment todo-app-backend -o yaml | grep image
```

**Pass Criteria**:
- ✅ Pod status identified (Pending, CrashLoop, etc.)
- ✅ Root cause analysis provided
- ✅ Actionable suggestions given
- ✅ Diagnostic matches actual issue

#### T065: Update Environment via Natural Language

```bash
# Request: Change backend log level to DEBUG
kubectl-ai "set the backend log level environment variable to DEBUG"

# Generated command:
# kubectl set env deployment/todo-app-backend LOG_LEVEL=DEBUG

# Expected output:
# deployment.apps/todo-app-backend env updated

# Verify environment variable
kubectl get deployment todo-app-backend -o jsonpath='{.spec.template.spec.containers[0].env}' | jq '.[] | select(.name=="LOG_LEVEL")'

# Expected:
# {
#   "name": "LOG_LEVEL",
#   "value": "DEBUG"
# }

# Watch rollout (pods restart with new env)
kubectl rollout status deployment/todo-app-backend

# Verify logs show DEBUG level
kubectl logs -f deployment/todo-app-backend | grep -i debug
```

**Pass Criteria**:
- ✅ Environment variable identified correctly
- ✅ Deployment updated with new value
- ✅ Rolling update triggered automatically
- ✅ New pods inherit updated environment

---

### Section 2: Cluster Analysis & Insights (T066-T071)

#### T066: Cluster Health Status

```bash
# Request: What's the overall health of my cluster?
kubectl-ai "give me a cluster health report"

# AI analyzes and responds:
# "Cluster Health Report:
#  - Nodes: 1/1 Ready
#  - Pods: 10/10 Running
#  - CPU Usage: 35% (350m/1000m)
#  - Memory: 45% (461Mi/1Gi)
#  - Pending: 0
#  - Failing: 0
#  Status: HEALTHY"

# Manual verification:
kubectl get nodes -o wide
kubectl get pods -o wide
kubectl top nodes
kubectl top pods

# Expected output shows healthy status
```

**Pass Criteria**:
- ✅ All nodes in Ready status
- ✅ No pending or failing pods
- ✅ Resource usage within normal ranges
- ✅ No cluster-level issues detected

#### T067: Resource Usage Analysis

```bash
# Request: Which pods are using the most memory?
kubectl-ai "show me the pods using the most memory sorted by usage"

# AI response example:
# "Top 5 Memory Consumers:
#  1. todo-app-backend-xxx     512Mi (50%)
#  2. todo-app-frontend-yyy    256Mi (25%)
#  3. coredns-zzz              128Mi (15%)
#  4. kube-proxy-aaa           64Mi   (8%)
#  5. metrics-server-bbb       32Mi   (2%)"

# Verify with kubectl:
kubectl top pods --sort-by=memory

# Expected output:
# NAME                              CPU(cores)   MEMORY(bytes)
# todo-app-backend-xxx              10m          512Mi
# todo-app-frontend-yyy             5m           256Mi
# coredns-zzz                        1m           128Mi
# ...

# Analyze high memory usage:
kubectl describe pod todo-app-backend-xxx | grep -A 5 "Limits\|Requests"

# Check if limits need adjustment
kubectl set resources deployment todo-app-backend \
  --limits=cpu=1000m,memory=1Gi \
  --requests=cpu=250m,memory=512Mi
```

**Pass Criteria**:
- ✅ Resource usage identified and sorted
- ✅ Outliers detected and highlighted
- ✅ Capacity planning insights provided
- ✅ Scaling recommendations if needed

#### T068: Event Analysis & Anomalies

```bash
# Request: Show me all cluster events from the last hour
kubectl-ai "what events happened in the cluster in the last hour?"

# AI aggregates and responds:
# "Recent Events (1 hour):
#  - 3 pod startups
#  - 2 pod terminations
#  - 1 node drain event
#  - 0 failures or errors
#  Status: Normal activity"

# Verify events:
kubectl get events --sort-by='.lastTimestamp' | tail -20

# Expected output shows recent activity

# Check for warnings/errors:
kubectl get events --field-selector type=Warning

# Expected: Minimal or no warnings
```

**Pass Criteria**:
- ✅ Events aggregated and summarized
- ✅ Anomalies highlighted
- ✅ Timestamps and context provided
- ✅ Actionable insights on abnormal patterns

#### T069: Configuration Drift Detection

```bash
# Request: Are there any deployments not matching their intended spec?
kubectl-ai "check if any deployments have drifted from their desired state"

# AI response:
# "Configuration Check:
#  - todo-app-backend: HEALTHY (3/3 replicas, all pods ready)
#  - todo-app-frontend: HEALTHY (1/1 replicas, pod ready)
#  - No drift detected
#  Recommendation: Continue monitoring"

# Verify specific deployment:
kubectl rollout status deployment/todo-app-backend

# Expected: Deployment shows desired == current == ready

# Check deployment replicas vs actual:
kubectl get deployment -o wide

# Verify no manual pod modifications:
kubectl get pods -o json | jq '.items[] | select(.metadata.annotations."deployment.kubernetes.io/revision" != null)'

# Expected: All pods managed by deployments (no orphaned pods)
```

**Pass Criteria**:
- ✅ Desired replicas match actual running pods
- ✅ No manual pod modifications detected
- ✅ All pods ready and healthy
- ✅ Helm releases in sync with cluster state

#### T070: Cost Analysis & Optimization

```bash
# Request: Which deployments are over-provisioned?
kubectl-ai "identify deployments that might be over-provisioned"

# AI response:
# "Resource Optimization Opportunities:
#  - todo-app-frontend: Current limits 500m CPU / 512Mi RAM
#    Actual usage: 5m CPU / 256Mi RAM
#    Recommendation: Reduce limits to 100m / 256Mi (saves ~60%)
#
#  - todo-app-backend: Current limits 1000m CPU / 1Gi RAM
#    Actual usage: 50m CPU / 450Mi RAM
#    Recommendation: Reduce limits to 500m / 512Mi (saves ~50%)"

# Check current resource allocation:
kubectl get deployment -o wide --show-labels

# Analyze with top commands:
kubectl top deployment

# Update resources for optimization:
kubectl set resources deployment/todo-app-frontend \
  --limits=cpu=100m,memory=256Mi
```

**Pass Criteria**:
- ✅ Over-provisioned resources identified
- ✅ Cost optimization recommendations provided
- ✅ Changes can be applied without disruption
- ✅ Actual vs. allocated usage tracked

#### T071: Dependency & Network Analysis

```bash
# Request: Which pods are communicating with each other?
kubectl-ai "show me the network communication patterns between pods"

# AI response:
# "Pod Communication Map:
#  - Frontend (port 3000) → Ingress: incoming traffic
#  - Ingress → Frontend (3000): incoming requests
#  - Frontend ↔ Backend (8000): API calls
#  - Backend → Database (external): SQL queries
#  - Backend → Cohere API (external): LLM calls
#  Status: All expected connections present"

# Verify with network policies:
kubectl get networkpolicies

# Check service endpoints:
kubectl get endpoints

# Monitor network traffic (if available):
kubectl top pod --containers

# Analyze ingress routing:
kubectl get ingress -o wide
```

**Pass Criteria**:
- ✅ Pod dependencies identified correctly
- ✅ External service calls accounted for
- ✅ Network policies allowing expected traffic
- ✅ No blocked or unexpected connections

---

### Section 3: Troubleshooting & Diagnostics (T072-T074)

#### T072: Automated Troubleshooting

```bash
# Request: The backend is experiencing errors, can you diagnose?
kubectl-ai "the backend pod is crashing, what's the problem?"

# AI performs diagnosis:
# 1. Gets pod status
# 2. Reads recent logs
# 3. Checks events
# 4. Analyzes environment
# 5. Provides diagnosis

# Possible response:
# "Diagnosis: Backend Pod Crash
#  Error: Database connection timeout
#  Root Cause: DATABASE_URL environment variable missing
#  Solution: Verify secret 'todo-secrets' exists and contains DATABASE_URL
#  Command: kubectl get secret todo-secrets
#  Next Steps: Recreate secret if missing"

# Implement suggested fix:
kubectl get secret todo-secrets

# If missing, recreate:
kubectl create secret generic todo-secrets \
  --from-literal=DATABASE_URL="postgresql://..."

# Restart deployment:
kubectl rollout restart deployment/todo-app-backend

# Verify fix:
kubectl logs -f deployment/todo-app-backend | head -20
```

**Pass Criteria**:
- ✅ Root cause identified correctly
- ✅ Diagnostic steps provided
- ✅ Solution actionable and specific
- ✅ Fix resolves the issue

#### T073: Performance Troubleshooting

```bash
# Request: Why is the backend pod slow?
kubectl-ai "the backend is responding slowly, what could be the issue?"

# AI analyzes performance:
# "Performance Analysis:
#  - CPU Usage: 850m (85% of limit)
#  - Memory: 490Mi (95% of limit)
#  - Disk I/O: High write operations
#  Issues Found:
#    1. Pod approaching CPU limit (potential throttling)
#    2. Pod approaching memory limit (risk of OOMKill)
#    3. Database queries may be slow
#  Recommendations:
#    1. Increase CPU limit from 1000m to 2000m
#    2. Increase memory limit from 512Mi to 1Gi
#    3. Check slow query logs on database
#    4. Consider adding caching layer"

# Check actual metrics:
kubectl top pod <backend-pod-name>

# Describe pod to see limits:
kubectl describe pod <backend-pod-name> | grep -A 5 "Limits\|Requests"

# Increase resources:
kubectl set resources deployment/todo-app-backend \
  --limits=cpu=2000m,memory=1Gi \
  --requests=cpu=500m,memory=512Mi

# Monitor metrics:
kubectl top pod -w
```

**Pass Criteria**:
- ✅ Performance metrics analyzed
- ✅ Bottlenecks identified (CPU, memory, I/O)
- ✅ Root causes determined
- ✅ Scaling/optimization recommendations provided

#### T074: Incident Response & Remediation

```bash
# Request: There's a service outage, help me recover
kubectl-ai "the API is down, how do I quickly restore service?"

# AI provides incident response steps:
# "Incident: API Service Outage
#  Severity: CRITICAL
#
#  Quick Recovery Steps:
#  1. Check pod status: kubectl get pods -l app=todo-app-backend
#  2. If CrashLoop: kubectl describe pod <pod> (check events)
#  3. If ImagePullError: Verify image exists in registry
#  4. If Not Ready: Check health endpoint: kubectl logs <pod>
#  5. If looks healthy: Try rollout restart
#  6. Last resort: Rollback to previous version
#
#  Status Page Update:
#  - Estimated recovery time: 2 minutes
#  - User communication: See status page template"

# Implement immediate recovery:
kubectl rollout restart deployment/todo-app-backend

# Monitor recovery:
kubectl rollout status deployment/todo-app-backend -w

# Check if service is accessible:
for i in {1..10}; do
  curl -s http://localhost:8000/health && echo "✓ API UP" && break
  sleep 2
done

# If still down, rollback to previous version:
kubectl rollout history deployment/todo-app-backend

# Expected output:
# REVISION  CHANGE-CAUSE
# 1         <previous>
# 2         <current>

# Rollback:
kubectl rollout undo deployment/todo-app-backend --to-revision=1

# Verify:
curl http://localhost:8000/health
```

**Pass Criteria**:
- ✅ Root cause identified quickly
- ✅ Recovery steps provided in priority order
- ✅ Service restored to healthy state
- ✅ Incident timeline documented for post-mortem

---

## Part 2: kagent Integration (Advanced Analysis)

### Installation & Setup

```bash
# Install kagent
pip install kagent

# Configure API keys
export OPENAI_API_KEY="sk-..."
export COHERE_API_KEY="sk-..."

# Initialize kagent
kagent init

# Configure for Kubernetes
kagent config --provider openai --model gpt-4
```

### Using kagent for Cluster Analysis

```bash
# Comprehensive cluster analysis
kagent analyze cluster

# Expected output: 10-20 minute detailed report covering:
# - Overall health (nodes, pods, resources)
# - Performance bottlenecks
# - Cost optimization opportunities
# - Security issues
# - Recommended actions (prioritized)

# Specific analyses
kagent analyze deployment todo-app-backend
kagent analyze pod <pod-name>
kagent analyze network
kagent analyze security
```

---

## Part 3: Chat API Integration with AIOps

### Using the Todo Chat API for Cluster Operations

```bash
# Example: Use chat endpoint to manage tasks alongside cluster operations

# Create task via chat:
curl -X POST http://localhost:8000/api/chat/send \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "content": "Create a task to scale backend to 5 replicas and monitor CPU usage"
  }'

# AI agent will:
# 1. Parse intent (create task)
# 2. Create task in database
# 3. Respond with confirmation

# Chat response:
# "✅ Task created: 'scale backend to 5 replicas and monitor CPU usage' (ID: 42)"

# Later, execute the scaling via chat:
curl -X POST http://localhost:8000/api/chat/send \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "content": "remind me about the scaling task, and execute kubectl-ai to scale backend"
  }'

# Integration creates unified workflow:
# Chat → Task Management → kubectl-ai → Cluster Operations → Monitoring → Chat Updates
```

---

## Summary: Phase 5 AIOps Checklist

| Task | Command | Expected Outcome |
|------|---------|------------------|
| T060: Scale Deployment | `kubectl-ai "scale backend to 3"` | Replicas updated |
| T061: Get Pod Logs | `kubectl-ai "show backend errors"` | Logs displayed |
| T062: Restart Pod | `kubectl-ai "restart backend"` | Rolling restart complete |
| T063: Port Forward | `kubectl-ai "forward port 8000"` | Local access established |
| T064: Pod Status | `kubectl-ai "why is pod failing?"` | Diagnosis provided |
| T065: Update Environment | `kubectl-ai "set LOG_LEVEL=DEBUG"` | Env updated, pods restarted |
| T066: Cluster Health | `kubectl-ai "cluster health report"` | Status summary |
| T067: Resource Usage | `kubectl-ai "top memory users"` | Sorted pod list |
| T068: Events Analysis | `kubectl-ai "recent events"` | Event summary |
| T069: Drift Detection | `kubectl-ai "config drift check"` | Status confirmed |
| T070: Cost Analysis | `kubectl-ai "over-provisioned pods"` | Recommendations |
| T071: Network Analysis | `kubectl-ai "pod communication"` | Network map |
| T072: Troubleshooting | `kubectl-ai "backend is crashing"` | Diagnosis + solution |
| T073: Performance | `kubectl-ai "backend is slow"` | Analysis + scaling advice |
| T074: Incident Response | `kubectl-ai "service outage"` | Recovery steps |

---

## Key Benefits of AIOps

✅ **Reduced MTTR** (Mean Time To Recovery): Instant diagnosis and recommended fixes
✅ **Natural Language Interface**: No need to memorize kubectl syntax
✅ **24/7 Availability**: Automated monitoring and alerts
✅ **Knowledge Base**: Captured expertise in AI models
✅ **Reproducible**: Same issue gets same diagnosis/solution
✅ **Integration**: Works with existing Kubernetes tools

---

**Phase 5 AIOps Complete**: kubectl-ai and kagent fully integrated for autonomous cluster operations, diagnostics, and optimization.

**Next Phase**: Phase 7 - Zero-Downtime Deployment Demonstrations
