# Integrate OpenAI Agents Skill

Name: Integrate OpenAI Agents

Instructions:
Setup & run OpenAI Agents SDK inside FastAPI chat endpoint

Responsibilities:
- Build message array from DB conversation history + new user message
- Run agent with MCP tools registered
- Parse tool calls, execute them, collect results
- Generate natural language response with confirmations
- Save full assistant response + tool results to DB
- Return {response, tool_calls} to frontend

Strict rules:
- Use gpt-4o-mini or gpt-4o (configurable via env)
- Inject user_id context for tools
- Always add friendly confirmation (e.g. "Task added!", "Marked complete!")
- Handle tool errors gracefully in response
- Keep endpoint fully stateless – DB holds everything

Current project: Phase III Todo AI Chatbot

## Implementation Steps

1. Create agent module in `/backend/agent/`
2. Implement chat endpoint with conversation history retrieval
3. Register MCP tools with the OpenAI Agent
4. Build message array from DB history
5. Execute agent run and parse tool calls
6. Handle tool execution results and generate responses
7. Save responses back to DB
8. Return structured response to frontend

## Execution

This skill will coordinate with the AI Agent Engineer agent to implement the required functionality.