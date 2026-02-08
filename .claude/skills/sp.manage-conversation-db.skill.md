# Manage Conversation DB Skill

Name: Manage Conversation DB

Instructions:
Handle stateless conversation persistence in Neon DB

Responsibilities:
- Create or load conversation by ID (or new if missing)
- Save user & assistant messages with role/content/timestamp
- Fetch full history for agent input (last N messages)
- Update conversation updated_at on every message
- Use async SQLModel sessions

Strict rules:
- All operations async
- Filter by user_id for security
- Never keep state in memory – always query DB
- Limit history fetch to avoid token overflow (e.g. last 20–30 messages)

Current project: Phase III – stateless chat with DB-persisted context

## Implementation Steps

1. Create conversation models in SQLModel for messages and conversations
2. Implement async CRUD operations for conversation management
3. Create conversation loading/creation functions
4. Implement message saving with role, content, and timestamps
5. Build history fetching with message limits
6. Add user_id filtering for security
7. Update timestamps on all operations

## Execution

This skill will coordinate with the Database Engineer agent to implement the required functionality.