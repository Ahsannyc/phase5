# Neon DB Connection Skill

Name: Neon DB Connection

Instructions:
Reusable async SQLModel + Neon PostgreSQL connection for FastAPI

Responsibilities:
- Create async engine from DATABASE_URL env var
- Replace postgresql:// with postgresql+asyncpg://
- Provide get_session dependency (AsyncSession)
- Add create_db_and_tables helper for startup

Strict rules:
- Always async
- Use echo=True only in dev
- No blocking calls

Current project: Phase 2 – Neon serverless DB integration

## Implementation Steps

1. Create database connection module in `/backend/app/db/`
2. Implement async engine creation with proper URL transformation
3. Create get_session dependency for FastAPI
4. Implement create_db_and_tables helper function
5. Add environment-specific configuration for echo setting
6. Ensure all database operations are asynchronous
7. Test connection establishment and session handling

## Execution

This skill will coordinate with the Database Engineer agent to implement the required functionality.