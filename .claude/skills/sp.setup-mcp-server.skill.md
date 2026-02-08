# Setup MCP Server Skill

Name: Setup MCP Server

Instructions:
Setup stateless MCP Server in FastAPI using Official MCP SDK

Responsibilities:
- Expose exactly 5 tools: add_task, list_tasks, complete_task, delete_task, update_task
- Use params & return formats exactly as in @specs/mcp/tools.md
- Integrate SQLModel CRUD for all task operations
- Get user_id from JWT (via get_current_user dependency)
- Tools must be completely stateless – all state in Neon DB
- Support tool chaining (agent can call multiple in one turn)
- Handle errors gracefully inside tools (return {"error": "message"})

Strict rules:
- Never store session state in memory
- Always validate user_id ownership
- Follow MCP SDK conventions & official examples

Current project: Phase III AI Chatbot (FastAPI + OpenAI Agents + MCP + Neon DB)

## Implementation Steps

1. Create MCP server module in `/backend/mcp/`
2. Implement the 5 required tools with proper parameter validation
3. Connect tools to SQLModel CRUD operations
4. Ensure JWT user validation in each tool
5. Make all tools stateless with database-backed persistence
6. Test tool chaining capability

## Execution

This skill will coordinate with the MCP Engineer agent to implement the required functionality.