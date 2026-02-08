# Research Findings: Todo AI Chatbot

## Overview
This document captures research findings for the Todo AI Chatbot implementation, addressing key technical decisions and unknowns identified during planning.

## 1. Cohere API Integration

### Decision: Use Cohere's chat completions API as the primary LLM
- **Rationale**: The specification explicitly states Cohere as the primary LLM for chat completions
- **Implementation**: Will use cohere-python SDK to connect to Cohere's chat API
- **Key considerations**: Need to handle API key securely via environment variables

### Alternatives considered:
- OpenAI GPT models
- Anthropic Claude
- Self-hosted models (Llama, Mistral)

## 2. OpenAI Agents SDK Integration

### Decision: Implement tool calling with OpenAI Agents SDK
- **Rationale**: Specification requires OpenAI Agents SDK for tool orchestration
- **Implementation**: Use the SDK to define tools that map to MCP operations
- **Key considerations**: Need to properly format tool definitions and handle tool call responses

### Alternatives considered:
- LangChain tool calling
- Custom tool orchestration
- Direct LLM prompting (without structured tools)

## 3. MCP (Model Context Protocol) Implementation

### Decision: Implement 5 MCP tools as specified
- **Rationale**: The specification defines exactly 5 tools that must be implemented via MCP SDK
- **Implementation**: Create an MCP server with stateless tools that interact with the database
- **Tools**: add_task, list_tasks, complete_task, delete_task, update_task

### Alternatives considered:
- REST API endpoints instead of MCP
- GraphQL mutations/queries
- Direct database access from agent

## 4. Database Design for Conversations

### Decision: Extend existing schema with Conversation and Message models
- **Rationale**: Need to persist conversation state as specified (stateless server requirement)
- **Implementation**: Add Conversation table (user_id, created_at, updated_at) and Message table (conversation_id, role, content)
- **Key considerations**: Proper indexing for performance, foreign key constraints for user isolation

### Database Models:
- Conversation: {id, user_id, created_at, updated_at}
- Message: {id, conversation_id, user_id, role, content, created_at}

## 5. Authentication & User Isolation

### Decision: Leverage existing Better Auth JWT infrastructure
- **Rationale**: Phase 2 already implements Better Auth with JWT tokens
- **Implementation**: Verify JWT on all endpoints and ensure user_id matches the resource owner
- **Key considerations**: All database queries must filter by user_id to prevent cross-user access

## 6. Frontend Chat Interface

### Decision: Implement OpenAI ChatKit-style UI with floating icon
- **Rationale**: Specification requires ChatKit-style interface with floating chat button
- **Implementation**: Create a slide-in or modal chat panel with message bubbles
- **Design elements**: Cyan/purple glow, glassmorphism, pulsing animation for idle state

## 7. Statelessness Requirement

### Decision: Implement true statelessness with database persistence
- **Rationale**: Specification requires stateless server with conversation state only in DB
- **Implementation**: Load conversation history from DB for each request, save responses back to DB
- **Benefits**: Scalability, resilience to server restarts, persistence across sessions

## 8. Error Handling Strategy

### Decision: Implement graceful error handling with user-friendly messages
- **Rationale**: Chatbot must handle various error conditions gracefully
- **Implementation**: Catch exceptions in tool calls and return meaningful error messages to the user
- **Examples**: Task not found, unauthorized access, database errors

## 9. AI Agent Behavior Configuration

### Decision: Configure agent with system prompt emphasizing confirmations
- **Rationale**: Specification requires always confirming actions and asking for clarification
- **Implementation**: Define system prompt that guides the AI behavior
- **Key elements**: Friendly tone, confirmation requests, clarification when ambiguous, error handling

## 10. Deployment Considerations

### Decision: Deploy MCP server separately from main backend
- **Rationale**: MCP tools may need to run in a different environment or scale independently
- **Implementation**: Separate FastAPI application for MCP server
- **Considerations**: Network connectivity between components, security, monitoring