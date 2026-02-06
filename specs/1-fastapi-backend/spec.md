# Backend Specification v1.0
Backend-Only – FastAPI + SQLModel + Neon PostgreSQL

Date: February 2026
Version: v1.0
Status: Ready for immediate implementation by Backend Engineer and Database Engineer agents

## 1. Overview & Purpose

Build a **secure, scalable backend** for the multi-user Todo web application using **FastAPI**, **SQLModel**, and **Neon Serverless PostgreSQL**.

This specification covers **only the backend layer**:
- User authentication endpoints (signup/signin – integrated with Better Auth)
- RESTful API for the 5 core Todo features with user isolation
- JWT verification middleware for protected routes
- Database schema, models, and CRUD operations
- Error handling and validation

The backend must integrate seamlessly with the frontend (as defined in @specs/ui/frontend-ai-themed-v1.md):
- Share BETTER_AUTH_SECRET for JWT issuance/validation
- Match expected API endpoints and payloads
- Handle CORS for frontend origin (BETTER_AUTH_URL=http://localhost:3000)
- Use Neon DB connection string for persistence

No frontend code, no deployment configuration, and no advanced features are included.

Environment variables (from .env):
- BETTER_AUTH_SECRET=CX7yA3GgjBJkdy5M5WR9nt4SvdCEUOA0
- BETTER_AUTH_URL=http://localhost:3000
- DATABASE_URL=postgresql://neondb_owner:npg_GtQsRu0KT3eE@ep-holy-mouse-aj1nsvqk-pooler.c-3.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require

## 2. The 5 Core Todo Features (must be fully implemented)

The backend must support these features via REST API, with strict user isolation (tasks filtered by authenticated user_id):

1. **Add / Create task**
   Create a new task owned by the authenticated user (title required, description optional).

2. **View / List tasks**
   Retrieve all tasks belonging only to the authenticated user.

3. **Update / Edit task**
   Modify title and/or description of a task (only if owned by authenticated user).

4. **Delete task**
   Remove a task (only if owned by authenticated user).

5. **Mark Complete / Toggle completion**
   Toggle the completed status of a task (only if owned by authenticated user).

All operations must:
- Validate ownership (403 if not owner)
- Use async DB sessions
- Return appropriate HTTP status codes and error messages

## 3. Core Requirements & Constraints

- Framework: FastAPI (async routes)
- ORM: SQLModel (Pydantic-integrated models)
- Database: Neon PostgreSQL (serverless, use provided DATABASE_URL)
- Authentication: JWT verification using BETTER_AUTH_SECRET (shared with frontend Better Auth)
- Middleware: Global dependency for JWT on protected routes
- Validation: Pydantic for request bodies
- No external auth libraries beyond FastAPI deps (use PyJWT for decoding)
- No advanced features: no search, filters, priorities, due dates
- Performance: async queries, indexes on user_id and completed
- Security: user isolation, no SQL injection, proper error masking
- Logging: basic Uvicorn logging

## 4. API Endpoints (match frontend expectations)

All endpoints under /api/ prefix.
Protected endpoints require valid JWT (401 if invalid/missing).

### Authentication (public)
- POST /api/auth/signup
  - Body: { email: str, password: str, name?: str }
  - Response: 201 { user: { id: int, email: str }, token: str }

- POST /api/auth/signin
  - Body: { email: str, password: str }
  - Response: 200 { user: { id: int, email: str }, token: str }

(Note: Integrate with Better Auth – backend handles user creation/validation, issues JWT matching frontend format with 'sub' = user_id)

### Tasks (protected)
- GET /api/tasks
  - Query params: none
  - Response: 200 [Task...] (filtered by user_id)

- POST /api/tasks
  - Body: { title: str, description?: str }
  - Response: 201 Task

- GET /api/tasks/{id}
  - Response: 200 Task (403 if not owner)

- PUT /api/tasks/{id}
  - Body: { title?: str, description?: str }
  - Response: 200 Task (403 if not owner)

- DELETE /api/tasks/{id}
  - Response: 204 No Content (403 if not owner)

- PATCH /api/tasks/{id}/complete
  - Body: { completed: bool }
  - Response: 200 Task (403 if not owner)

## 5. Database Schema & Models

Use SQLModel for models.
Migrate with Alembic.

Tables:
- users
  - id: int (PK, auto-increment)
  - email: str (unique, indexed)
  - password_hash: str (hashed with bcrypt or argon2)
  - name?: str
  - created_at: datetime (default now)

- tasks
  - id: int (PK, auto-increment)
  - user_id: int (FK to users.id, indexed)
  - title: str
  - description?: str
  - completed: bool (default False)
  - created_at: datetime (default now)
  - updated_at: datetime (default now, on update now)

Indexes:
- tasks: (user_id, completed)
- users: email

## 6. JWT Middleware & Security

- Dependency: async def get_current_user(token: str = Depends(OAuth2PasswordBearer(tokenUrl="token")))
  - Decode JWT with BETTER_AUTH_SECRET
  - Extract user_id from 'sub'
  - Validate expiry/alg (HS256)
  - Raise 401 if invalid

- For task routes: add param user_id: int = Path(...) → check matches JWT user_id (403 if not)
- CORS: allow origin from BETTER_AUTH_URL, credentials=True

## 7. Error Handling

- ValidationError → 400 with details
- Invalid JWT → 401 {"detail": "Invalid token"}
- Not owner → 403 {"detail": "Not authorized"}
- Not found → 404 {"detail": "Task not found"}
- Server error → 500 minimal info

## 8. Non-Functional Requirements

- Async everything: routes, DB sessions (AsyncSession)
- Env vars: load from .env (use pydantic-settings)
- Startup: create tables if not exist (SQLModel.metadata.create_all)
- Testing: basic Pytest setup (later phase)

## 9. Acceptance Criteria

- Signup/signin creates user + issues valid JWT
- All 5 core features work via API (tested with Postman or curl)
- User isolation enforced (cannot access other users' tasks)
- Integrates with frontend: frontend can call endpoints with JWT
- No 500 errors on valid inputs
- DB persists data (test with Neon console)

## 10. References

- Obey constitution.md
- Align with @specs/ui/frontend-ai-themed-v1.md (API shapes)
- Use skills: @skills/neon-db-connection.py, @skills/jwt-auth-middleware.py

This specification is self-contained for building a complete, secure backend that integrates perfectly with the frontend.