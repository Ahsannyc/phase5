# System Architecture

## Overview

The Todo App is a cloud-native, multi-tier application with AI-powered task management.

```
┌─────────────────────────────────────────────────────────────────┐
│                        Client Layer                             │
├─────────────────────────────────────────────────────────────────┤
│  Web Browser (React/Next.js)  │  Mobile App (Future)            │
│  http://localhost:3000        │  iOS/Android SDKs               │
└────────────────┬──────────────────────────┬──────────────────────┘
                 │                          │
       ┌─────────┴──────────┐       ┌───────┴─────────┐
       │                    │       │                 │
┌──────┴──────┐  ┌──────────┴──────┐  ┌──────────────┐│
│   Ingress   │  │   Load Balancer │  │  WAF (Opt)  ││
│  (Nginx)    │  │                 │  │             ││
└──────┬──────┘  └────────┬────────┘  └──────┬───────┘┘
       │                  │                   │
       └──────────────────┼───────────────────┘
                          │
                ┌─────────▼─────────┐
                │   API Gateway     │
                │ (Kong/AWS API GW) │
                └────────┬──────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
┌───────▼──────┐  ┌────────▼───────┐  ┌───▼────────┐
│  Frontend    │  │    Backend     │  │  ChatBot   │
│  Service     │  │    Service     │  │  Service   │
│ (Next.js)    │  │   (FastAPI)    │  │  (Agent)   │
│ :3000        │  │   :8000        │  │            │
└──────────────┘  └────────┬───────┘  └────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        │         ┌────────▼────────┐        │
        │         │   Application   │        │
        │         │   Database      │        │
        │         │  (PostgreSQL)   │        │
        │         │  @Neon.tech     │        │
        │         └─────────────────┘        │
        │                                    │
        └────────────────┬───────────────────┘
                         │
        ┌────────────────┼──────────────────┐
        │                │                  │
    ┌───▼────┐     ┌─────▼──────┐    ┌──────▼───┐
    │ Cohere │     │  OpenAI    │    │  Vault   │
    │  API   │     │    API     │    │(Secrets) │
    └────────┘     └────────────┘    └──────────┘
```

---

## Component Architecture

### Frontend (Next.js)

```
┌─────────────────────────────────────┐
│       Next.js Application           │
├─────────────────────────────────────┤
│  Pages/Routes                       │
│  ├─ /login (authentication)         │
│  ├─ /dashboard (task list)          │
│  └─ /chat (AI chatbot)              │
├─────────────────────────────────────┤
│  Components                         │
│  ├─ TaskList                        │
│  ├─ TaskForm                        │
│  ├─ ChatInterface (OpenAI ChatKit)  │
│  └─ AuthGuard                       │
├─────────────────────────────────────┤
│  Services                           │
│  ├─ API Client (centralized)        │
│  ├─ Auth (JWT, Better Auth)         │
│  └─ State Management (Context API)  │
├─────────────────────────────────────┤
│  Build: `pnpm build`                │
│  Output: `.next/standalone/`        │
└─────────────────────────────────────┘
```

### Backend (FastAPI)

```
┌─────────────────────────────────────┐
│       FastAPI Application           │
├─────────────────────────────────────┤
│  API Routes                         │
│  ├─ /api/auth (signup/login)        │
│  ├─ /api/tasks (CRUD)               │
│  └─ /api/chat (AI chat)             │
├─────────────────────────────────────┤
│  Middleware                         │
│  ├─ Authentication (JWT)            │
│  ├─ CORS                            │
│  └─ Rate Limiting                   │
├─────────────────────────────────────┤
│  Services                           │
│  ├─ TaskService (CRUD logic)        │
│  ├─ ChatService (AI integration)    │
│  └─ AuthService (JWT tokens)        │
├─────────────────────────────────────┤
│  Database                           │
│  ├─ SQLModel ORM                    │
│  └─ AsyncIO + asyncpg               │
├─────────────────────────────────────┤
│  External APIs                      │
│  ├─ Cohere (LLM)                    │
│  ├─ OpenAI (Embeddings)             │
│  └─ Secret Store (Vault)            │
├─────────────────────────────────────┤
│  Server: `uvicorn app.main:app`     │
│  Workers: 4 (production)            │
└─────────────────────────────────────┘
```

### Database Schema

```
┌──────────────┐        ┌──────────────┐        ┌──────────────┐
│    Users     │        │    Tasks     │        │   Messages   │
├──────────────┤        ├──────────────┤        ├──────────────┤
│ id (PK)      │◄───┐   │ id (PK)      │        │ id (PK)      │
│ email (UK)   │    │   │ user_id (FK) │        │ conversation │
│ name         │    │   │ title        │        │ _id (FK)     │
│ password_hash│    └───┤ description  │        │ role         │
│ created_at   │        │ completed    │        │ content      │
│ updated_at   │        │ created_at   │        │ tool_calls   │
└──────────────┘        │ updated_at   │        │ created_at   │
                        └──────────────┘        └──────────────┘
                                 ▲                      ▲
                                 │                      │
                                 │                      │
                        ┌──────────────┐        ┌──────────────┐
                        │Conversations │        │   (Messages  │
                        ├──────────────┤        │   belong to  │
                        │ id (PK)      │────────┤ Conversation)│
                        │ user_id (FK) │        └──────────────┘
                        │ title        │
                        │ created_at   │
                        │ updated_at   │
                        └──────────────┘
```

---

## Kubernetes Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Kubernetes Cluster                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Ingress Controller (nginx)              │  │
│  │  Route: /         → todo-app-frontend:3000          │  │
│  │  Route: /api/*    → todo-app-backend:8000           │  │
│  └──────┬───────────────────────────────────────────────┘  │
│         │                                                   │
│  ┌──────┴────────────────────────────────────────────────┐ │
│  │              Service Mesh (Optional)                  │ │
│  │  - Traffic management                                │ │
│  │  - Circuit breaking                                  │ │
│  │  - Distributed tracing                               │ │
│  └──────┬──────────────────────────────────────────────┤ │
│         │                                              │ │
│  ┌──────▼──────┐                              ┌──────▼──┐ │
│  │  Frontend   │                              │ Backend │ │
│  │Deployment   │                              │Deployment
│  │(replicas:3) │◄────────(Services)─────────►│(replicas
│  │ ┌────────┐  │                              │  :3)   │ │
│  │ │ Pod 1  │  │                              │┌──────┐│ │
│  │ │ Pod 2  │  │                              ││Pod 1 ││ │
│  │ │ Pod 3  │  │                              ││Pod 2 ││ │
│  │ └────────┘  │                              ││Pod 3 ││ │
│  └─────────────┘                              │└──────┘│ │
│                                               └────────┘ │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │              ConfigMaps & Secrets                │  │
│  │  - DATABASE_URL                                  │  │
│  │  - API Keys (COHERE, OPENAI)                    │  │
│  │  - AUTH_SECRET                                   │  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │         Persistent Volumes (Optional)             │  │
│  │  - Logs                                           │  │
│  │  - Cache                                          │  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │     Monitoring & Observability Stack             │  │
│  │  - Prometheus (metrics)                          │  │
│  │  - Grafana (dashboards)                          │  │
│  │  - Loki (logs)                                   │  │
│  │  - Jaeger (traces)                               │  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## Data Flow Diagrams

### Task Creation Flow

```
┌─────────────┐
│   User      │
│  (Browser)  │
└──────┬──────┘
       │ 1. Click "Add Task" → Opens form
       │
       ▼
┌──────────────────────┐
│  Frontend Component  │
│  (TaskForm)          │
└──────┬───────────────┘
       │ 2. User enters task details
       │
       ▼
┌──────────────────────────────────┐
│  API Client                      │
│  POST /api/tasks                 │
│  + Authorization header (JWT)    │
└──────┬───────────────────────────┘
       │ 3. HTTP Request
       │
       ▼
┌──────────────────────────────────┐
│  Backend API                     │
│  TaskService.create_task()       │
│  - Validate input               │
│  - Check user permissions       │
│  - Store in database            │
└──────┬───────────────────────────┘
       │ 4. Save to DB
       │
       ▼
┌──────────────────────────────────┐
│  PostgreSQL Database             │
│  INSERT INTO tasks (...)         │
└──────┬───────────────────────────┘
       │ 5. Return task object
       │
       ▼
┌──────────────────────────────────┐
│  Frontend                        │
│  Update task list (UI refresh)   │
│  Show success message            │
└──────────────────────────────────┘
```

### Chat Task Creation Flow

```
┌────────────────┐
│  User          │
│ (ChatKit UI)   │
└────────┬───────┘
         │ 1. Type: "create task buy groceries"
         │
         ▼
┌───────────────────────────────────┐
│  Frontend                         │
│  POST /api/chat/send              │
│  {"content": "create task..."}    │
└────────┬────────────────────────┬─┘
         │                        │
         │ HTTP POST             │ WebSocket (optional)
         │                        │
         ▼                        ▼
┌──────────────────────────────────────────┐
│  Backend Chat Endpoint                   │
│  1. Save user message to DB             │
│  2. Parse intent (add_task)             │
│  3. Extract parameters                   │
└────────┬─────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────┐
│  Agent Runner                            │
│  1. Recognize intent                     │
│  2. Call TodoTools.add_task()            │
│  3. Get AI response                      │
└────────┬─────────────────────────────────┘
         │
         ├─────────────────┬─────────────────┐
         │                 │                 │
         ▼                 ▼                 ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ TodoTools    │  │ Cohere API   │  │ Database     │
│ add_task()   │  │ (fallback)    │  │ (save)       │
│ Insert task  │  │ LLM response  │  │              │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       │                 │                  │
       └────────┬────────┴──────────────────┘
                │
                ▼
┌────────────────────────────────────────────┐
│  Save assistant response to DB             │
│  "✅ Task added: 'buy groceries' (ID: 3)" │
└────────┬───────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────┐
│  Return to Frontend                        │
│  Display AI response in chat               │
│  Update task list                          │
└────────────────────────────────────────────┘
```

---

## Deployment Targets

### Development
```
Local Machine
├─ Docker Compose
├─ Frontend: http://localhost:3000
├─ Backend: http://localhost:8000
└─ Database: PostgreSQL (Docker)
```

### Staging
```
Minikube / Local Kubernetes
├─ Helm Chart Deployment
├─ Frontend: http://todo.local
├─ Backend: http://todo.local/api
├─ Database: Neon PostgreSQL
└─ Monitoring: Prometheus + Grafana
```

### Production
```
Cloud Kubernetes (EKS/GKE/AKS)
├─ Multi-zone deployment
├─ Frontend: https://app.example.com
├─ Backend API: https://api.example.com
├─ Database: Managed PostgreSQL (RDS/Cloud SQL)
├─ Cache: Redis (optional)
├─ CDN: CloudFront / Cloud CDN
├─ Monitoring: Full observability stack
├─ Logging: ELK / GCP Cloud Logging
├─ Secrets: AWS Secrets Manager / GCP Secret Manager
└─ Backups: Automated daily backups
```

---

## Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | Next.js 14 | SSR/SSG, React components |
| **Frontend UI** | Tailwind CSS | Responsive styling |
| **Frontend Chat** | OpenAI ChatKit | AI chatbot interface |
| **Backend** | FastAPI | REST API framework |
| **Backend Async** | asyncio, asyncpg | Async database access |
| **ORM** | SQLModel | Type-safe ORM |
| **Database** | PostgreSQL | Relational database |
| **Auth** | JWT, Better Auth | Authentication |
| **LLM** | Cohere | Natural language processing |
| **Embeddings** | OpenAI | Vector embeddings |
| **Container** | Docker | Container runtime |
| **Orchestration** | Kubernetes | Container orchestration |
| **Package Mgr** | Helm | K8s package management |
| **Monitoring** | Prometheus | Metrics collection |
| **Dashboards** | Grafana | Metrics visualization |
| **Logging** | Loki | Log aggregation |
| **Tracing** | Jaeger | Distributed tracing |

---

## Security Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Security Layers                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Layer 1: TLS/HTTPS                                        │
│  ├─ All traffic encrypted in transit                       │
│  └─ TLS 1.3+ enforced                                      │
│                                                             │
│  Layer 2: Authentication (JWT)                             │
│  ├─ Tokens expire after 24 hours                           │
│  ├─ Refresh tokens valid 7 days                            │
│  └─ Secure token storage in HttpOnly cookies              │
│                                                             │
│  Layer 3: Authorization (RBAC)                             │
│  ├─ User isolation (tasks belong to user)                  │
│  ├─ Service accounts for K8s                               │
│  └─ Least privilege principle                              │
│                                                             │
│  Layer 4: Secret Management                                │
│  ├─ Secrets stored in Vault / Cloud Secrets                │
│  ├─ Encrypted at rest                                      │
│  ├─ Rotated regularly                                      │
│  └─ Never in code/images/logs                              │
│                                                             │
│  Layer 5: Container Security                               │
│  ├─ Non-root users (nginx:101, appuser:1000)              │
│  ├─ Read-only filesystems (where possible)                 │
│  ├─ Image scanning (Trivy)                                 │
│  └─ No secrets in image layers                             │
│                                                             │
│  Layer 6: Network Security                                 │
│  ├─ Network policies (ingress/egress)                      │
│  ├─ WAF rules (optional)                                   │
│  └─ DDoS protection (cloud provider)                       │
│                                                             │
│  Layer 7: Audit & Logging                                  │
│  ├─ All API calls logged                                   │
│  ├─ Authentication events tracked                          │
│  └─ Security events alerted                                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Performance Optimization

### Frontend
- ✅ Code splitting by route
- ✅ Image optimization (next/image)
- ✅ Caching strategies (SWR, React Query)
- ✅ CSS-in-JS elimination (Tailwind)

### Backend
- ✅ Database connection pooling (asyncpg)
- ✅ Query optimization (indexes)
- ✅ Caching (Redis, optional)
- ✅ Response compression (gzip)

### Infrastructure
- ✅ Multi-replica deployments
- ✅ Horizontal autoscaling
- ✅ CDN for static assets
- ✅ Database replication

---

## Scaling Strategy

### Vertical Scaling (Single Node)
- Increase CPU/memory limits
- Optimize queries
- Add caching

### Horizontal Scaling (Multiple Nodes)
- Scale replicas: `kubectl scale deployment/todo-app-backend --replicas=5`
- Load balancing (automatic with Services)
- Database read replicas

### Database Scaling
- Connection pooling (PgBouncer)
- Read replicas for queries
- Sharding (if needed)
- Archive old data

