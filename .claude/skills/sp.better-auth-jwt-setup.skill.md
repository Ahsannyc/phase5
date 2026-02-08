# Better Auth JWT Setup Skill

Name: Better Auth JWT Setup

Instructions:
Setup Better Auth with JWT plugin in Next.js

Responsibilities:
- Configure createAuth with secret from env
- Export signIn, signUp, useSession, authMiddleware
- Enable JWT plugin
- Handle session & token in client & server components

Strict rules:
- Use process.env.BETTER_AUTH_SECRET
- Protect all private routes with authMiddleware
- Store token securely (no localStorage fallback)

Current project: Phase 2 – frontend authentication layer

## Implementation Steps

1. Create Better Auth configuration in `/frontend/src/lib/auth/`
2. Configure createAuth with JWT plugin and environment secret
3. Export authentication functions (signIn, signUp, useSession)
4. Implement authMiddleware for route protection
5. Create session handling for both client and server components
6. Implement secure token storage mechanism
7. Set up protected route patterns
8. Test authentication flow in different component contexts

## Execution

This skill will coordinate with the Frontend Engineer agent to implement the required functionality.