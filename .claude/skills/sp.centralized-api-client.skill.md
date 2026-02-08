# Centralized API Client Skill

Name: Centralized API Client

Instructions:
Reusable typed API client with automatic JWT attachment

Responsibilities:
- Create fetch wrapper in lib/api.ts
- Get token from useSession()
- Add Authorization: Bearer header automatically
- Handle 401 → redirect to signin
- Support typed responses (Task[], Task, etc.)
- Include loading/error states where needed

Strict rules:
- Use Next.js fetch (not axios)
- Always relative URLs (/api/...)
- TypeScript strict mode

Current project: Phase 2 – safe API calls from frontend

## Implementation Steps

1. Create API client module in `/frontend/src/lib/api.ts`
2. Implement fetch wrapper with automatic JWT token attachment
3. Integrate with useSession() for token retrieval
4. Add Authorization: Bearer header automatically
5. Implement 401 error handling with redirect to signin
6. Create TypeScript interfaces for typed responses
7. Add loading and error state management
8. Test API calls with various response types
9. Ensure all URLs are relative to the API

## Execution

This skill will coordinate with the Frontend Engineer agent to implement the required functionality.