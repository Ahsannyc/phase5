# Configure ChatKit Skill

Name: Configure ChatKit

Instructions:
Setup & configure OpenAI ChatKit in Next.js frontend

Responsibilities:
- Add NEXT_PUBLIC_OPENAI_DOMAIN_KEY to .env
- Create ChatKit component / wrapper
- POST messages to /api/{user_id}/chat endpoint
- Pass & receive conversation_id (persist in localStorage or URL)
- Show loading indicator during API call
- Display user & assistant messages with AI-themed styling
- Visualize tool results (e.g. "Task added: Buy groceries")
- Integrate with Better Auth session for JWT & user_id

Strict rules:
- Only show ChatKit after login (protected route)
- Use centralized api client with auto JWT
- Match glassmorphism, cyan/purple neon, dark AI theme
- Handle 401 → redirect to signin

Current project: Phase III – ChatKit UI on top of Phase 2 frontend

## Implementation Steps

1. Update .env with NEXT_PUBLIC_OPENAI_DOMAIN_KEY
2. Create ChatKit component with proper styling
3. Implement message posting to /api/{user_id}/chat endpoint
4. Add conversation_id persistence in localStorage or URL
5. Create loading indicators for API calls
6. Style user and assistant messages with AI theme
7. Visualize tool results appropriately
8. Integrate with Better Auth session
9. Implement protected route logic
10. Add 401 error handling for redirects

## Execution

This skill will coordinate with the ChatKit Frontend Agent to implement the required functionality.