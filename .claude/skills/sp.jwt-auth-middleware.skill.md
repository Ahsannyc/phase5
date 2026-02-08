# JWT Auth Middleware Skill

Name: JWT Auth Middleware

Instructions:
FastAPI dependency to verify JWT and extract user_id

Responsibilities:
- Use OAuth2PasswordBearer(tokenUrl="token")
- Decode JWT with BETTER_AUTH_SECRET (HS256)
- Extract user_id from payload["sub"]
- Raise 401 on invalid/expired/missing token
- Return int user_id on success

Strict rules:
- Never trust URL user_id without JWT check
- Always validate token signature & expiry

Current project: Phase 2 – secure multi-user task isolation

## Implementation Steps

1. Create JWT authentication module in `/backend/app/auth/`
2. Implement OAuth2PasswordBearer token scheme
3. Create JWT decoding function with BETTER_AUTH_SECRET
4. Validate token signature and expiration
5. Extract user_id from payload["sub"]
6. Raise HTTPException(401) for invalid tokens
7. Return integer user_id for valid tokens
8. Test authentication flow with various scenarios

## Execution

This skill will coordinate with the Backend Engineer agent to implement the required functionality.