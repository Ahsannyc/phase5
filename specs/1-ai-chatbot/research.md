# Research Document: Todo AI Chatbot

## Decision: MCP Tools Implementation
**Rationale**: Following the specification and constitution requirements, we'll implement 5 MCP tools as stateless functions that interact with the database through existing CRUD operations. These tools will be registered with the MCP server and called by the AI agent when processing natural language commands.
**Alternatives considered**: Direct database calls from the agent (rejected per constitution - all task operations must go through MCP tools)

## Decision: Cohere API Integration
**Rationale**: The specification requires Cohere as the primary LLM for chat completions. We'll configure the OpenAI Agents SDK to use Cohere's API via a custom configuration that points to Cohere's endpoints.
**Alternatives considered**: Using OpenAI models directly (rejected as specification mandates Cohere as primary LLM)

## Decision: Conversation Persistence Strategy
**Rationale**: To achieve stateless server architecture as required by the constitution, conversation history will be loaded from the database for each request and saved after each interaction. This allows resumable conversations after refresh/server restart.
**Alternatives considered**: Session-based storage (rejected per constitution - server must be stateless)

## Decision: Frontend Chat Integration Approach
**Rationale**: Implement a floating chat icon that opens a slide-in panel with ChatKit-style interface. This matches the AI-themed design requirements while providing seamless integration with the existing UI.
**Alternatives considered**: Separate chat page (rejected as floating icon provides better accessibility)

## Decision: User Isolation Implementation
**Rationale**: Each MCP tool will validate that the user owns the tasks being operated on. The chat endpoint will validate JWT and ensure user_id in URL matches the authenticated user.
**Alternatives considered**: No alternative - this is mandated by the constitution for security