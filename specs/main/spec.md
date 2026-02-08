# Phase 3 – Todo AI Chatbot
High-Level Specification v1.0
Full Integration with Phase 2 Full-Stack Todo App

Date: February 2026
Version: v1.0
Status: Foundation for Backend Engineer, AI Agent Engineer, ChatKit Frontend Agent, MCP Engineer

## 1. Overview & Purpose

Build a **conversational AI chatbot** that allows users to manage their personal Todo list using **natural language** after login.

The chatbot must:
- Fully support the **5 core Todo features** through conversation
- Appear as a floating/chat icon in the Phase 2 frontend UI
- Open a modern, AI-themed chat interface (using OpenAI ChatKit style)
- Be powered by **Cohere** (primary LLM) + **OpenAI Agents SDK** (tool orchestration)
- Use **MCP SDK** to expose task operations as tools
- Maintain conversation context via database (stateless server)
- Enforce strict user isolation (only manage own tasks)

This specification covers:
- Backend chat endpoint & integration
- MCP tools for task operations
- AI agent behavior & Cohere integration
- Frontend chat icon & conversation UI
- Database extensions for conversation persistence

No new advanced features beyond the 5 core Todo actions.

## 2. The 5 Core Todo Features (via Natural Language)

The chatbot must understand and correctly execute:

1. **Add / Create task**
   Examples: "Add task buy groceries", "Remember to call mom", "I need to pay bills"

2. **View / List tasks**
   Examples: "Show my tasks", "What's pending?", "List completed tasks"

3. **Update / Edit task**
   Examples: "Change task 1 to buy groceries and milk", "Update meeting time"

4. **Delete task**
   Examples: "Delete task 3", "Remove old meeting"

5. **Mark Complete / Toggle completion**
   Examples: "Mark task 2 done", "Complete call mom"

Behavior requirements:
- Always confirm actions (e.g. "Added: Buy groceries!", "Task 3 marked complete ✓")
- Handle ambiguity gracefully (ask clarifying questions)
- If multiple matches (e.g. delete), list first then confirm
- Graceful error handling (e.g. "Task not found", "That's not your task")

## 3. Core Requirements & Constraints

- Backend: FastAPI (reuse Phase 2)
- LLM: Cohere (primary – chat completions) via COHERE_API_KEY
- Agent framework: OpenAI Agents SDK (tool calling & orchestration)
- MCP: Official MCP SDK (5 stateless tools)
- Database: Neon PostgreSQL + SQLModel (add Conversation & Message models)
- Frontend: Next.js (reuse Phase 2) + OpenAI ChatKit style UI
- Auth: Better Auth (JWT) – user_id from token
- Stateless server: conversation state only in DB
- Chat icon: Floating button (bottom-right, cyan glow) → opens chat panel
- No new external UI libraries beyond ChatKit components

## 4. Frontend Chat Integration

- Add floating chat icon (AI-themed: cyan glow, pulse when idle)
- On click → open slide-in or modal chat panel
- Use OpenAI ChatKit-like UI: message bubbles, typing indicator
- Show user messages (right-aligned), assistant messages (left)
- Display tool results naturally (e.g. "✓ Task added: Buy groceries")
- Persist conversation_id in localStorage or URL param
- Send POST to /api/{user_id}/chat with {message, conversation_id?}
- Show loading animation during response
- Handle errors: show red toast ("Sorry, something went wrong")

## 5. Backend Chat Endpoint

- POST /api/{user_id}/chat
- Body: { message: string, conversation_id?: integer }
- Response: { conversation_id: int, response: string, tool_calls?: array }

Flow (stateless):
1. Validate JWT → get user_id
2. Get or create conversation
3. Load history (last N messages)
4. Store user message
5. Build messages array for agent
6. Run OpenAI Agents SDK agent (Cohere model)
7. Execute any tool calls (MCP tools)
8. Store assistant response
9. Return response to frontend

## 6. MCP Tools (5 Tools)

Exactly these tools (stateless, DB-backed):

1. **add_task**
   Params: user_id (string), title (string), description (string?)

2. **list_tasks**
   Params: user_id (string), status ("all" | "pending" | "completed")

3. **complete_task**
   Params: user_id (string), task_id (integer)

4. **delete_task**
   Params: user_id (string), task_id (integer)

5. **update_task**
   Params: user_id (string), task_id (integer), title? (string), description? (string)

All tools:
- Validate ownership (user_id match)
- Return structured result (task_id, status, title) or error

## 7. AI Agent Behavior

- Primary model: Cohere (via COHERE_API_KEY)
- Use OpenAI Agents SDK for tool calling & chaining
- System prompt must include:
  - Friendly, concise, natural tone
  - Always confirm actions
  - Ask for clarification if ambiguous
  - Use tools only when clear intent
  - Handle errors in response ("Sorry, I couldn't find that task...")

## 8. Database Extensions

Add to Phase 2 schema:

- Conversation: user_id, id, created_at, updated_at
- Message: conversation_id, user_id, role ("user"|"assistant"), content, created_at

Indexes: conversation_id, user_id

## 9. Acceptance Criteria

- User logs in → sees chat icon
- Click icon → opens chat panel
- Type "Add task call mom" → confirms + adds task
- Type "Show my tasks" → lists user's tasks
- Type "Mark task 1 done" → completes task
- Type "Delete task 2" → deletes after confirmation
- Conversation persists after refresh/restart
- No cross-user data access
- Errors shown gracefully in chat
- UI matches AI-themed design (cyan/purple glow, glassmorphism)

## 10. References & Rules

- Obey constitution.md at all times
- Reuse Phase 2 frontend/backend where possible
- Align with @specs/api/chat-endpoint.md (when created)
- Use skills: @skills/mcp-server-setup.py, @skills/openai-agents-integration.py, etc.

This specification is self-contained and sufficient for agents to implement a complete, integrated AI chatbot.