# Kubernetes Manifest Contracts

**Date**: 2026-02-08
**Feature**: 001-cloud-native-deploy
**Purpose**: Specify expected Kubernetes resource structure and configuration

---

## Deployment Contracts

### Frontend Deployment

**Name**: todo-frontend
**Replicas**: 1 (default, configurable via values.yaml)
**Image**: todo-frontend:latest
**Port**: 80 (exposed), 3000 (internal service)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-frontend
  labels:
    app: todo-frontend
spec:
  replicas: {{ .Values.frontend.replicas }}
  selector:
    matchLabels:
      app: todo-frontend
  template:
    metadata:
      labels:
        app: todo-frontend
    spec:
      containers:
      - name: frontend
        image: "{{ .Values.frontend.image.repository }}:{{ .Values.frontend.image.tag }}"
        imagePullPolicy: {{ .Values.frontend.image.pullPolicy }}
        ports:
        - containerPort: 80
        livenessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 10
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 5
          periodSeconds: 5
        resources:
          requests:
            memory: "64Mi"
            cpu: "250m"
          limits:
            memory: "128Mi"
            cpu: "500m"
        securityContext:
          runAsNonRoot: true
          runAsUser: 101
          allowPrivilegeEscalation: false
          capabilities:
            drop:
            - ALL
          readOnlyRootFilesystem: false  # nginx needs write to /tmp
      terminationGracePeriodSeconds: 30
      restartPolicy: Always
```

**Constraints**:
- Always run as non-root user (nginx UID 101)
- Probes check HTTP 200 on port 80
- Resource requests/limits defined
- Graceful termination: 30 seconds

---

### Backend Deployment

**Name**: todo-backend
**Replicas**: 1 (default, configurable via values.yaml)
**Image**: todo-backend:latest
**Port**: 8000

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-backend
  labels:
    app: todo-backend
spec:
  replicas: {{ .Values.backend.replicas }}
  selector:
    matchLabels:
      app: todo-backend
  template:
    metadata:
      labels:
        app: todo-backend
    spec:
      containers:
      - name: backend
        image: "{{ .Values.backend.image.repository }}:{{ .Values.backend.image.tag }}"
        imagePullPolicy: {{ .Values.backend.image.pullPolicy }}
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: {{ .Values.secretName }}
              key: DATABASE_URL
        - name: BETTER_AUTH_SECRET
          valueFrom:
            secretKeyRef:
              name: {{ .Values.secretName }}
              key: BETTER_AUTH_SECRET
        - name: COHERE_API_KEY
          valueFrom:
            secretKeyRef:
              name: {{ .Values.secretName }}
              key: COHERE_API_KEY
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: {{ .Values.secretName }}
              key: OPENAI_API_KEY
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 2
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 15
          periodSeconds: 5
          timeoutSeconds: 2
        lifecycle:
          preStop:
            exec:
              command: ["/bin/sh", "-c", "sleep 10"]
        resources:
          requests:
            memory: "256Mi"
            cpu: "500m"
          limits:
            memory: "512Mi"
            cpu: "1000m"
        securityContext:
          runAsNonRoot: true
          runAsUser: 1000
          allowPrivilegeEscalation: false
          capabilities:
            drop:
            - ALL
          readOnlyRootFilesystem: false  # FastAPI may write logs
      terminationGracePeriodSeconds: 30
      restartPolicy: Always
```

**Constraints**:
- Always run as non-root user (appuser UID 1000)
- Secrets injected as environment variables from Kubernetes Secret
- Probes check /health endpoint
- preStop hook allows graceful shutdown (10 second window for in-flight requests)
- terminationGracePeriodSeconds: 30 (matches preStop + request timeout)

---

## Service Contracts

### Frontend Service

**Name**: todo-frontend
**Type**: ClusterIP
**Selector**: app: todo-frontend

```yaml
apiVersion: v1
kind: Service
metadata:
  name: todo-frontend
  labels:
    app: todo-frontend
spec:
  type: ClusterIP
  selector:
    app: todo-frontend
  ports:
  - name: http
    port: 3000           # External port (within cluster)
    targetPort: 80       # Container port
    protocol: TCP
```

**Constraints**:
- ClusterIP type (internal routing within cluster)
- External port 3000 (convention for frontend)
- Maps to container port 80 (nginx)

---

### Backend Service

**Name**: todo-backend
**Type**: ClusterIP
**Selector**: app: todo-backend

```yaml
apiVersion: v1
kind: Service
metadata:
  name: todo-backend
  labels:
    app: todo-backend
spec:
  type: ClusterIP
  selector:
    app: todo-backend
  ports:
  - name: http
    port: 8000          # External port (within cluster)
    targetPort: 8000    # Container port
    protocol: TCP
```

**Constraints**:
- ClusterIP type (internal routing within cluster)
- Port mapping 8000:8000 (FastAPI default)

---

## Ingress Contract

**Name**: todo-app (ingressClassName: nginx)
**Host**: todo.local (configurable via values.yaml)
**Paths**: / → frontend, /api/* → backend

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: todo-app
  labels:
    app: todo-app
spec:
  ingressClassName: nginx
  rules:
  - host: {{ .Values.ingress.host }}
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: todo-backend
            port:
              number: 8000
      - path: /
        pathType: Prefix
        backend:
          service:
            name: todo-frontend
            port:
              number: 3000
  tls: []  # Phase 4: no TLS; future hardening
```

**Constraints**:
- nginx ingressClassName (requires Minikube addon: `minikube addons enable ingress`)
- Path-based routing: /api/* to backend, / to frontend
- Host header matching (todo.local)
- No TLS in Phase 4 (local dev only)

**Access**: After setting up /etc/hosts:
```bash
echo "<minikube-ip> todo.local" >> /etc/hosts
curl http://todo.local/         # → frontend
curl http://todo.local/api/health  # → backend
```

---

## Secret Contract

**Name**: todo-secrets (referenced in Deployments)
**Keys**: BETTER_AUTH_SECRET, COHERE_API_KEY, DATABASE_URL, OPENAI_API_KEY

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: {{ .Values.secretName }}
type: Opaque
data:
  BETTER_AUTH_SECRET: {{ .Values.secrets.betterAuthSecret | b64enc }}
  COHERE_API_KEY: {{ .Values.secrets.cohereApiKey | b64enc }}
  DATABASE_URL: {{ .Values.secrets.databaseUrl | b64enc }}
  OPENAI_API_KEY: {{ .Values.secrets.openaiApiKey | b64enc }}
```

**Constraints**:
- Opaque type (no special handling)
- Data is base64-encoded (Helm b64enc filter)
- Never committed to Git; values provided at deploy time
- Referenced by Deployments via envFrom or individual env entries

**Validation**:
```bash
# View secret metadata (not values)
kubectl get secret todo-secrets

# Describe secret (shows keys, not values)
kubectl describe secret todo-secrets

# Decode a value (for debugging)
kubectl get secret todo-secrets -o jsonpath='{.data.DATABASE_URL}' | base64 -d

# Set secret from .env file
kubectl create secret generic todo-secrets --from-file=.env
```

---

## Pod Disruption Budget (Optional, Phase 4 AIOps)

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: todo-backend-pdb
spec:
  minAvailable: 1
  selector:
    matchLabels:
      app: todo-backend
```

**Purpose**: Prevent Kubernetes from evicting all backend pods during maintenance (e.g., node drain). This will be generated via kubectl-ai as part of AIOps demo.

---

## Resource Requests & Limits

### Frontend Deployment

- **Requests**: 64Mi memory, 250m CPU
- **Limits**: 128Mi memory, 500m CPU
- **Rationale**: nginx is lightweight; serving static files requires little compute

### Backend Deployment

- **Requests**: 256Mi memory, 500m CPU
- **Limits**: 512Mi memory, 1000m CPU
- **Rationale**: FastAPI + SQLModel + LLM calls require more resources; limits prevent noisy neighbor issues

---

## Health Check Contracts

### Frontend Readiness & Liveness

```yaml
livenessProbe:
  httpGet:
    path: /
    port: 80
  initialDelaySeconds: 10
  periodSeconds: 10
  timeoutSeconds: 1
  failureThreshold: 3
readinessProbe:
  httpGet:
    path: /
    port: 80
  initialDelaySeconds: 5
  periodSeconds: 5
  timeoutSeconds: 1
  failureThreshold: 1
```

- **Liveness**: Ensures container is running; fails after 3 consecutive failures (30 seconds)
- **Readiness**: Ensures traffic is routed; fails after 1 failure (5 seconds)

### Backend Readiness & Liveness

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 30  # Extra time for app startup
  periodSeconds: 10
  timeoutSeconds: 2
  failureThreshold: 3
readinessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 15  # Wait for DB connection
  periodSeconds: 5
  timeoutSeconds: 2
  failureThreshold: 1
```

- **Liveness**: Ensures app is alive; fails after 3 failures (30 seconds) → pod restart
- **Readiness**: Ensures app is ready to serve traffic; fails after 1 failure (5 seconds) → removed from service endpoints

---

## Validation & Testing

### Helm Lint & Validate

```bash
helm lint ./k8s/helm/todo-app
helm template todo-app ./k8s/helm/todo-app > manifests.yaml
# Review manifests.yaml for correctness
```

### kubectl Validation

```bash
# Check deployment status
kubectl get deployments -o wide
kubectl describe deployment todo-frontend

# Check pod status
kubectl get pods -o wide
kubectl logs pod/todo-frontend-<hash>

# Check service endpoints
kubectl get service
kubectl describe service todo-backend

# Check ingress rules
kubectl get ingress
kubectl describe ingress todo-app

# Check secret exists
kubectl get secret todo-secrets
```

### Runtime Validation

```bash
# Port-forward for testing (if ingress not working)
kubectl port-forward svc/todo-frontend 3000:3000
kubectl port-forward svc/todo-backend 8000:8000

# Test health checks
kubectl exec pod/todo-backend-<hash> -- curl http://localhost:8000/health
```

---

## Scaling Contract

Default 1 replica each. Scaling via:

```bash
# Manual scale
kubectl scale deployment todo-backend --replicas=3

# Via Helm values
helm upgrade todo-app ./k8s/helm/todo-app --set backend.replicas=3

# Via kubectl-ai (Phase 4 AIOps)
kubectl-ai "scale deployment todo-backend to 3 replicas"
```

Expected behavior:
- New pods created and reach Running state within 10 seconds
- Load balancer (Service) distributes traffic to all 3 pods
- No downtime during scale-up (rolling update not needed for stateless app)
