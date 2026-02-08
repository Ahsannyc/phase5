# Production Deployment Runbook

**Document**: Production Operations Guide for Todo App
**Audience**: DevOps, SREs, On-Call Engineers
**Updated**: 2026-02-08
**Criticality**: CRITICAL

## Overview

This runbook provides step-by-step procedures for deploying and operating the Todo App in production environments (EKS, GKE, AKS).

---

## Table of Contents

1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Production Environment Setup](#production-environment-setup)
3. [Deployment Procedures](#deployment-procedures)
4. [Rollback Procedures](#rollback-procedures)
5. [Monitoring & Alerting](#monitoring--alerting)
6. [Incident Response](#incident-response)
7. [Operational Procedures](#operational-procedures)
8. [Security & Compliance](#security--compliance)

---

## Pre-Deployment Checklist

### Prerequisites Validation

```bash
# Run before ANY production deployment

# 1. Verify Kubernetes cluster access
kubectl cluster-info
# Expected: API server and CoreDNS running

# 2. Verify ingress controller
kubectl get pods -n ingress-nginx | grep ingress-nginx-controller
# Expected: Controller in Running state

# 3. Check available resources
kubectl top nodes
# Expected: Sufficient CPU/memory available

# 4. Verify persistent storage (if used)
kubectl get pvc
# Expected: All PVCs in Bound state (if applicable)

# 5. Verify database connectivity
# Run from admin pod:
kubectl run -it --rm debug --image=postgres:15 --restart=Never -- \
  psql -h $POSTGRES_HOST -U $POSTGRES_USER -d $POSTGRES_DB -c "SELECT 1"
# Expected: Returns 1 (connection successful)

# 6. Verify all secrets exist
kubectl get secret todo-secrets
# Expected: Secret present with all keys

# 7. Verify image registry access
kubectl create secret docker-registry gcr-secret \
  --docker-server=gcr.io \
  --docker-username=_json_key \
  --docker-password="$(cat /path/to/key.json)" \
  --docker-email=user@example.com
# Expected: Secret created successfully

# 8. Review configuration changes
git log --oneline -10
# Expected: See recent commits with deployment changes
```

### Configuration Validation

```bash
# Validate Helm chart before deployment
helm lint ./k8s/helm/todo-app

# Expected output:
# ==> Linting ./k8s/helm/todo-app
# [INFO] Chart is consistent
# 1 chart(s) linted, 0 error(s)

# Validate templates render correctly
helm template todo-app ./k8s/helm/todo-app --debug

# Validate values syntax
helm get values todo-app  # If upgrading existing

# Dry-run deployment
helm install todo-app ./k8s/helm/todo-app \
  --dry-run \
  --debug \
  --namespace production \
  -f values-production.yaml
```

### Pre-Flight Security Check

```bash
# Image scan
trivy image --severity HIGH,CRITICAL \
  gcr.io/my-project/todo-frontend:v1.0
trivy image --severity HIGH,CRITICAL \
  gcr.io/my-project/todo-backend:v1.0

# Expected: 0 HIGH/CRITICAL vulnerabilities

# Secret scan
gitleaks detect --source local --exit-code 1

# Expected: Exit code 0 (no secrets found)

# Check pod security policies
kubectl get psp
# Expected: Policies in place

# Verify RBAC configuration
kubectl auth can-i get pods \
  --as=system:serviceaccount:production:todo-app-backend

# Expected: yes
```

---

## Production Environment Setup

### 1. Create Production Namespace

```bash
# Create namespace
kubectl create namespace production

# Set namespace as default for subsequent commands
kubectl config set-context --current --namespace=production

# Verify
kubectl config view | grep current-context
```

### 2. Create Secrets

```bash
# Create secrets from secure storage
# NEVER hardcode in scripts - use secret management tools
# Options: AWS Secrets Manager, Azure Key Vault, Vault, etc.

# Example with AWS Secrets Manager:
SECRETS=$(aws secretsmanager get-secret-value \
  --secret-id prod/todo-app/secrets \
  --query SecretString \
  --output text)

# Create secret from retrieved values
kubectl create secret generic todo-secrets \
  --from-literal=DATABASE_URL="$(echo $SECRETS | jq -r .database_url)" \
  --from-literal=BETTER_AUTH_SECRET="$(echo $SECRETS | jq -r .auth_secret)" \
  --from-literal=COHERE_API_KEY="$(echo $SECRETS | jq -r .cohere_key)" \
  --from-literal=OPENAI_API_KEY="$(echo $SECRETS | jq -r .openai_key)" \
  -n production

# Verify secret created
kubectl get secret todo-secrets -n production
```

### 3. Configure Ingress

```bash
# Create TLS certificate secret
kubectl create secret tls todo-app-tls \
  --cert=/path/to/cert.pem \
  --key=/path/to/key.pem \
  -n production

# Or use cert-manager for automatic renewal:
helm repo add jetstack https://charts.jetstack.io
helm install cert-manager jetstack/cert-manager \
  --namespace cert-manager \
  --create-namespace \
  --set installCRDs=true

# Create Certificate resource:
cat <<EOF | kubectl apply -f -
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: todo-app-cert
  namespace: production
spec:
  secretName: todo-app-tls
  issuerRef:
    name: letsencrypt-prod
    kind: ClusterIssuer
  dnsNames:
  - todo.example.com
EOF

# Verify TLS certificate
kubectl get certificate -n production
```

### 4. Configure Monitoring & Logging

```bash
# Install Prometheus for metrics
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace

# Install ELK Stack or Loki for logging
helm repo add grafana https://grafana.github.io/helm-charts
helm install loki grafana/loki-stack \
  --namespace logging \
  --create-namespace

# Configure log forwarding (example with Fluentd)
helm install fluentd stable/fluentd \
  --namespace logging \
  --set elasticsearch.host=elasticsearch
```

---

## Deployment Procedures

### Initial Deployment (Fresh Cluster)

```bash
# Step 1: Add Helm repository
helm repo add todo https://charts.myregistry.com
helm repo update

# Step 2: Create values file for production
cat > values-production.yaml <<EOF
frontend:
  replicas: 3
  image:
    repository: gcr.io/my-project/todo-frontend
    tag: v1.0.0
    pullPolicy: IfNotPresent
  resources:
    limits:
      cpu: 500m
      memory: 512Mi
    requests:
      cpu: 250m
      memory: 256Mi

backend:
  replicas: 3
  image:
    repository: gcr.io/my-project/todo-backend
    tag: v1.0.0
    pullPolicy: IfNotPresent
  resources:
    limits:
      cpu: 1000m
      memory: 1Gi
    requests:
      cpu: 500m
      memory: 512Mi

ingress:
  enabled: true
  host: todo.example.com
  tls:
    enabled: true
    secretName: todo-app-tls
EOF

# Step 3: Deploy application
helm install todo-app ./k8s/helm/todo-app \
  -n production \
  -f values-production.yaml

# Step 4: Verify deployment
kubectl rollout status deployment/todo-app-frontend -n production -w
kubectl rollout status deployment/todo-app-backend -n production -w

# Step 5: Verify services
kubectl get svc -n production

# Step 6: Verify ingress
kubectl get ingress -n production

# Step 7: Test application
curl -H "Host: todo.example.com" https://api.example.com/api/health

# Expected: {"status":"healthy"}
```

### Upgrade Deployment (Rolling Update)

```bash
# Step 1: Update image tags in values-production.yaml
# Change frontend.image.tag and backend.image.tag to new version

# Step 2: Review changes
helm diff upgrade todo-app ./k8s/helm/todo-app \
  -n production \
  -f values-production.yaml

# Expected: Shows what will change (image versions, etc.)

# Step 3: Perform upgrade (zero-downtime rolling update)
helm upgrade todo-app ./k8s/helm/todo-app \
  -n production \
  -f values-production.yaml \
  --wait \
  --timeout 10m

# Step 4: Monitor rollout
kubectl rollout status deployment/todo-app-backend -n production -w

# Expected: All replicas updated, no service interruption

# Step 5: Verify health
for i in {1..5}; do
  curl -s https://todo.example.com/api/health | jq .
  sleep 5
done

# Expected: All requests return {"status":"healthy"}

# Step 6: Document upgrade
helm history todo-app -n production
```

### Scale Deployment

```bash
# Scale backend to handle increased load
kubectl scale deployment todo-app-backend \
  --replicas=5 \
  -n production

# Or via Helm:
helm upgrade todo-app ./k8s/helm/todo-app \
  -n production \
  -f values-production.yaml \
  --set backend.replicas=5 \
  --wait

# Monitor scaling
kubectl get pods -l app=todo-app-backend -n production -w

# Expected: New pods start up, old pods remain healthy during transition

# Verify load distribution
kubectl get endpoints todo-app-backend -n production

# Check metrics (if monitoring installed)
kubectl top pod -l app=todo-app-backend -n production
```

---

## Rollback Procedures

### Emergency Rollback (Service Down)

**Severity**: CRITICAL | **MTTR Target**: 2 minutes

```bash
# Step 1: Stop the bleeding (immediate action)
# If database issue: Kill long-running queries
# If memory leak: Reduce replicas to 1
kubectl scale deployment todo-app-backend --replicas=1 -n production

# Step 2: Check rollout history
helm history todo-app -n production

# Expected output:
# REVISION  UPDATED         STATUS          CHART           DESCRIPTION
# 1         Thu Jan 01...   DEPLOYED        todo-app-1.0.0  Install complete
# 2         Thu Jan 08...   SUPERSEDED      todo-app-1.0.0  Upgrade complete
# 3         Fri Feb 08...   DEPLOYED        todo-app-1.0.0  Upgrade complete (CURRENT)

# Step 3: Rollback to previous version
helm rollback todo-app 2 -n production

# Expected: Previous release restored

# Step 4: Verify rollback
kubectl rollout status deployment/todo-app-backend -n production -w

# Step 5: Test service
curl https://todo.example.com/api/health

# Expected: {"status":"healthy"}

# Step 6: Post-incident: Investigate failure
# - Check logs: kubectl logs -n production --tail=100
# - Check events: kubectl get events -n production
# - Analyze metrics: kubectl top pod -n production
# - Create incident ticket
```

### Planned Rollback (Issue Found During Testing)

```bash
# Step 1: Verify current version
helm list -n production

# Step 2: List available revisions
helm history todo-app -n production

# Step 3: Review the version to rollback to
helm show values todo-app --version 1.0.0

# Step 4: Rollback
helm rollback todo-app 2 -n production

# Step 5: Monitor and test
kubectl rollout status deployment/todo-app-backend -n production -w
curl https://todo.example.com/api/health

# Step 6: Communicate to stakeholders
# "Rolled back to previous version due to [reason]"
# "Service restored at [timestamp]"
```

---

## Monitoring & Alerting

### Key Metrics to Monitor

```yaml
# Deployment Metrics
- Pod restart count (should be 0)
- Pod CPU/memory usage (should be <80% of limits)
- Pod readiness (should be 100%)
- Rollout status (should be complete)

# Application Metrics
- API response time p95 (target: <200ms)
- API error rate (target: <0.1%)
- Database connection pool usage (target: <80%)
- Cache hit rate (target: >80%)

# Kubernetes Metrics
- Node CPU/memory (should be <70%)
- Disk usage (should be <80%)
- Network I/O (should be <50% of bandwidth)
```

### Prometheus Alerts

```yaml
# Create PrometheusRule for alerting
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: todo-app-alerts
spec:
  groups:
  - name: todo.rules
    rules:
    # Pod alerts
    - alert: PodNotReady
      expr: kube_pod_status_ready{namespace="production", pod=~"todo-app-.*"} == 0
      for: 2m
      annotations:
        summary: "Pod {{ $labels.pod }} is not ready"

    - alert: PodRestarts
      expr: rate(kube_pod_container_status_restarts_total{namespace="production", pod=~"todo-app-.*"}[15m]) > 0
      for: 5m
      annotations:
        summary: "Pod {{ $labels.pod }} is restarting"

    # Resource alerts
    - alert: HighMemoryUsage
      expr: |
        (sum(container_memory_usage_bytes{namespace="production", pod=~"todo-app-.*"})
         / sum(container_spec_memory_limit_bytes{namespace="production", pod=~"todo-app-.*"}))
        > 0.9
      for: 5m
      annotations:
        summary: "High memory usage in {{ $labels.namespace }}"

    - alert: HighCPUUsage
      expr: |
        (sum(rate(container_cpu_usage_seconds_total{namespace="production", pod=~"todo-app-.*"}[5m]))
         / sum(container_spec_cpu_quota{namespace="production", pod=~"todo-app-.*"} / container_spec_cpu_period{namespace="production"}))
        > 0.8
      for: 5m
      annotations:
        summary: "High CPU usage in {{ $labels.namespace }}"

    # Application alerts
    - alert: HighErrorRate
      expr: |
        (sum(rate(http_requests_total{namespace="production", status=~"5.."}[5m]))
         / sum(rate(http_requests_total{namespace="production"}[5m])))
        > 0.01
      for: 5m
      annotations:
        summary: "High error rate (>1%)"

    - alert: ServiceDown
      expr: up{job="todo-app", namespace="production"} == 0
      for: 1m
      annotations:
        summary: "Service is down"
        severity: critical
```

### Manual Monitoring Commands

```bash
# Check pod status
kubectl get pods -n production -w

# View pod logs
kubectl logs -f deployment/todo-app-backend -n production

# Monitor resource usage
kubectl top pod -n production --containers

# Check events
kubectl get events -n production --sort-by='.lastTimestamp'

# Check deployment status
kubectl rollout status deployment/todo-app-backend -n production

# Query metrics (if Prometheus installed)
kubectl exec -it prometheus-0 -n monitoring -- \
  promtool query instant \
  'rate(http_requests_total[5m])'
```

---

## Incident Response

### Incident Template

```markdown
## Incident Report: [Service Name] [Date/Time]

### Summary
- Duration: [start] to [resolution]
- MTTR: [Mean Time To Recovery]
- User Impact: [percentage of users affected]

### Timeline
- [T+0] Issue detected (automated alert / user report)
- [T+5] Investigation started
- [T+10] Root cause identified
- [T+15] Mitigation applied
- [T+20] Service restored

### Root Cause
[Technical analysis of what went wrong]

### Remediation
[Steps taken to fix the issue]

### Prevention
[Changes to prevent recurrence]

### Post-Incident Actions
- [ ] Update runbook
- [ ] Deploy fix to production
- [ ] Update monitoring/alerting
- [ ] Schedule post-mortem
```

### Common Issues & Resolutions

#### Issue: Backend Pod CrashLoopBackOff

```bash
# Diagnosis
kubectl describe pod <pod-name> -n production
kubectl logs <pod-name> -n production --previous

# Common causes:
# 1. Database connection failed
#    → Verify DATABASE_URL in secret
#    → Test connectivity: psql $DATABASE_URL

# 2. Missing dependencies
#    → Check requirements.txt in image
#    → Rebuild image with all dependencies

# 3. Health check timeout
#    → Increase initialDelaySeconds in deployment
#    → Check logs for startup errors

# Resolution
kubectl set env deployment/todo-app-backend \
  INIT_DELAY_SECONDS=60 -n production

kubectl rollout restart deployment/todo-app-backend -n production
```

#### Issue: High Memory Usage / OOMKilled

```bash
# Diagnosis
kubectl top pod -n production
kubectl describe pod <pod-name> | grep -A 10 "Last State"

# Common causes:
# 1. Memory leak in application
#    → Check application logs for unusual behavior
#    → Profile with tools like pympler (Python)

# 2. Insufficient limit
#    → Increase memory limit in Helm values
#    → Monitor actual usage vs limit

# Resolution
helm upgrade todo-app ./k8s/helm/todo-app \
  -n production \
  -f values-production.yaml \
  --set backend.resources.limits.memory=2Gi
```

#### Issue: Service Latency Spike

```bash
# Diagnosis
kubectl top pod -n production
kubectl top node -n production
kubectl logs -f deployment/todo-app-backend -n production | grep -i "slow\|timeout"

# Common causes:
# 1. Database slow queries
#    → Check database query logs
#    → Run EXPLAIN on slow queries
#    → Add indexes if needed

# 2. Resource contention (CPU/memory)
#    → Scale up: increase replicas
#    → Increase resource limits

# 3. Network issues
#    → Check network policies
#    → Verify DNS resolution

# Resolution
# Immediate: Scale up
kubectl scale deployment todo-app-backend --replicas=5 -n production

# Long-term: Optimize
# - Optimize slow database queries
# - Add caching layer
# - Increase resource allocations
```

---

## Operational Procedures

### Database Migrations

```bash
# Step 1: Schedule maintenance window
# Announce on status page: "Scheduled maintenance 02:00 UTC"

# Step 2: Scale down to 1 replica
kubectl scale deployment todo-app-backend --replicas=1 -n production

# Step 3: Run migration job
kubectl apply -f - <<EOF
apiVersion: batch/v1
kind: Job
metadata:
  name: db-migration-$(date +%s)
  namespace: production
spec:
  template:
    spec:
      serviceAccountName: todo-app-backend
      containers:
      - name: migration
        image: gcr.io/my-project/todo-backend:v1.0.0
        command: ["alembic", "upgrade", "head"]
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: todo-secrets
              key: DATABASE_URL
      restartPolicy: Never
  backoffLimit: 3
EOF

# Step 4: Monitor job
kubectl logs -f job/db-migration-* -n production

# Step 5: Scale back up
kubectl scale deployment todo-app-backend --replicas=3 -n production

# Step 6: Verify application works
curl https://todo.example.com/api/health
```

### Backup & Disaster Recovery

```bash
# Daily database backup (automated via cron)
0 2 * * * /scripts/backup-db.sh >> /var/log/backup.log 2>&1

# Backup script example
#!/bin/bash
BACKUP_DIR="/backups/database"
BACKUP_FILE="$BACKUP_DIR/todo-db-$(date +%Y%m%d-%H%M%S).sql.gz"

# Export DATABASE_URL from secret
export DATABASE_URL=$(kubectl get secret todo-secrets -n production -o jsonpath='{.data.DATABASE_URL}' | base64 -d)

# Perform backup
pg_dump $DATABASE_URL | gzip > $BACKUP_FILE

# Upload to cloud storage
aws s3 cp $BACKUP_FILE s3://my-backup-bucket/

# Keep local backups for 7 days
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete

echo "Backup completed: $BACKUP_FILE"

# Restore from backup (if needed)
BACKUP_FILE="s3://my-backup-bucket/todo-db-20260208-020000.sql.gz"
aws s3 cp $BACKUP_FILE - | gunzip | psql $DATABASE_URL
```

### Scheduled Maintenance

```bash
# Rolling restart (no downtime, checks configuration)
kubectl rollout restart deployment/todo-app-backend -n production
kubectl rollout status deployment/todo-app-backend -n production -w

# Node maintenance (drain & cordon)
# Step 1: Mark node as unavailable
kubectl cordon node-name

# Step 2: Drain workloads
kubectl drain node-name --ignore-daemonsets --delete-emptydir-data

# Step 3: Perform maintenance
# ... run updates, patches, etc ...

# Step 4: Return node to service
kubectl uncordon node-name

# Step 5: Verify pods reschedule
kubectl get pods -o wide | grep node-name
```

---

## Security & Compliance

### Secret Rotation

```bash
# Monthly secret rotation (Database password, API keys)

# Step 1: Generate new secret
NEW_PASSWORD=$(openssl rand -base64 32)

# Step 2: Create new secret (don't delete old one yet)
kubectl create secret generic todo-secrets-v2 \
  --from-literal=DATABASE_URL="postgresql://user:${NEW_PASSWORD}@..." \
  --from-literal=BETTER_AUTH_SECRET="..." \
  -n production

# Step 3: Update deployment to use new secret
kubectl patch deployment todo-app-backend \
  -p '{"spec":{"template":{"spec":{"containers":[{"name":"todo-backend","env":[{"name":"DATABASE_URL","valueFrom":{"secretKeyRef":{"name":"todo-secrets-v2"}}}]}]}}}}' \
  -n production

# Step 4: Monitor rollout
kubectl rollout status deployment/todo-app-backend -n production -w

# Step 5: Delete old secret
kubectl delete secret todo-secrets -n production

# Step 6: Update secret management system
# Update secret in AWS Secrets Manager / HashiCorp Vault
```

### Compliance Checks

```bash
# PCI-DSS Compliance
- [ ] All secrets encrypted at rest
- [ ] All communication over TLS
- [ ] All secrets rotated quarterly
- [ ] Access logs maintained for 90 days

# GDPR Compliance
- [ ] User data can be exported
- [ ] User data can be deleted
- [ ] Consent management implemented
- [ ] Data retention policies enforced

# CIS Kubernetes Benchmark
- [ ] Network policies configured
- [ ] Pod security policies enforced
- [ ] RBAC enabled
- [ ] Audit logging enabled
```

---

## On-Call Runbook

### On-Call Escalation

```
Level 1: Frontend/Backend Engineer (30 min response time)
- Basic troubleshooting (logs, metrics, restarts)
- Engage if: Pod restarts, Memory leak, Basic connectivity

Level 2: SRE/DevOps (15 min response time)
- Infrastructure issues (node, network, storage)
- Engage if: Node failure, Persistent storage issues, Network partition

Level 3: Lead SRE (5 min response time)
- Critical system failures
- Engage if: Data loss risk, Total outage, Security incident
```

### First Response Checklist

```bash
#!/bin/bash
# On-call first response script

echo "=== Emergency Incident Response ==="
echo "Time: $(date)"
echo "Severity: $1"  # CRITICAL / HIGH / MEDIUM

# Gather data
echo "=== System Status ==="
kubectl get nodes -n production
kubectl get pods -n production --sort-by=.status.startTime | tail -20

echo "=== Application Health ==="
for i in {1..3}; do
  curl -s https://todo.example.com/api/health | jq .
  sleep 1
done

echo "=== Resource Usage ==="
kubectl top nodes
kubectl top pod -n production

echo "=== Recent Events ==="
kubectl get events -n production --sort-by='.lastTimestamp' | tail -20

echo "=== Pod Logs ==="
kubectl logs -n production --all-containers=true --previous=false -l app=todo-app-backend | tail -50

# Decide action
echo "=== Recommended Actions ==="
# [Will be filled based on symptoms]
```

---

## Appendix: Useful Commands

```bash
# Deployment
helm install APP ./chart -n NAMESPACE -f values.yaml
helm upgrade APP ./chart -n NAMESPACE -f values.yaml
helm rollback APP REVISION -n NAMESPACE

# Pods
kubectl get pods -n NAMESPACE -w
kubectl logs POD -n NAMESPACE -f
kubectl exec POD -n NAMESPACE -- COMMAND
kubectl describe pod POD -n NAMESPACE

# Resources
kubectl top pod -n NAMESPACE
kubectl top node
kubectl get pvc -n NAMESPACE

# Networking
kubectl get svc -n NAMESPACE
kubectl get ingress -n NAMESPACE
kubectl port-forward svc/SERVICE 8080:8080 -n NAMESPACE

# Scaling
kubectl scale deployment APP --replicas=3 -n NAMESPACE
kubectl autoscale deployment APP --min=2 --max=5 -n NAMESPACE

# Updates
kubectl set image deployment APP container=IMAGE -n NAMESPACE
kubectl set env deployment APP KEY=VALUE -n NAMESPACE
kubectl patch deployment APP -p '{"spec":{"replicas":3}}' -n NAMESPACE
```

---

**Document Revision**: v1.0
**Last Updated**: 2026-02-08
**Next Review**: 2026-03-08
**Owner**: DevOps Team
**Feedback**: Please submit issues or improvements via [link to issue tracker]

