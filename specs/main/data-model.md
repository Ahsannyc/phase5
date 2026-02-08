# Data Model: Todo AI Chatbot

## Overview
This document defines the data models for the Todo AI Chatbot, extending the existing Todo application schema to support conversations and AI interactions.

## Entity Relationships

### User (existing from Phase 2)
- **Table**: `users`
- **Fields**:
  - `id` (int, primary key, autoincrement)
  - `email` (str, unique, indexed)
  - `username` (str, unique, indexed)
  - `password_hash` (str)
  - `created_at` (datetime)
  - `updated_at` (datetime)

### Task (existing from Phase 2)
- **Table**: `tasks`
- **Fields**:
  - `id` (int, primary key, autoincrement)
  - `title` (str, not null)
  - `description` (str, nullable)
  - `completed` (bool, default false)
  - `user_id` (int, foreign key to users.id, not null)
  - `created_at` (datetime)
  - `updated_at` (datetime)
- **Relationships**:
  - Belongs to one User
  - One User has many Tasks

### Conversation (NEW for Phase 3)
- **Table**: `conversations`
- **Fields**:
  - `id` (int, primary key, autoincrement)
  - `user_id` (int, foreign key to users.id, not null)
  - `title` (str, nullable) - Auto-generated from first message or summary
  - `created_at` (datetime)
  - `updated_at` (datetime)
- **Relationships**:
  - Belongs to one User
  - One User has many Conversations
  - One Conversation has many Messages

### Message (NEW for Phase 3)
- **Table**: `messages`
- **Fields**:
  - `id` (int, primary key, autoincrement)
  - `conversation_id` (int, foreign key to conversations.id, not null)
  - `user_id` (int, foreign key to users.id, not null)
  - `role` (str, enum: "user" | "assistant" | "tool", not null)
  - `content` (str, not null)
  - `tool_calls` (JSON, nullable) - Serialized tool call objects
  - `tool_responses` (JSON, nullable) - Serialized tool response objects
  - `created_at` (datetime)
- **Relationships**:
  - Belongs to one Conversation
  - Belongs to one User
  - One Conversation has many Messages

## Indexes
- `users.email` (unique)
- `users.username` (unique)
- `tasks.user_id` (indexed)
- `conversations.user_id` (indexed)
- `conversations.created_at` (indexed)
- `messages.conversation_id` (indexed)
- `messages.user_id` (indexed)
- `messages.created_at` (indexed)

## Validation Rules
1. **User Isolation**: All queries must filter by `user_id` to ensure users only access their own data
2. **Task Ownership**: When creating/updating/deleting tasks, validate that `user_id` matches authenticated user
3. **Conversation Ownership**: When accessing conversations/messages, validate that `user_id` matches authenticated user
4. **Role Validation**: `role` field in messages must be one of "user", "assistant", or "tool"
5. **Required Fields**: All non-nullable fields must be provided

## State Transitions
1. **Task Completion**:
   - `completed` field transitions from `false` to `true`
   - Triggered by `complete_task` MCP tool

2. **Message Creation**:
   - New message with `role` = "user" when user sends message
   - New message with `role` = "assistant" when AI responds
   - New message with `role` = "tool" when tool calls are executed

## API Access Patterns
1. **Get User's Conversations**: Filter conversations by `user_id`
2. **Get Conversation Messages**: Filter messages by `conversation_id` and verify `user_id` ownership
3. **Add Message**: Create new message with current user's `user_id` and specified `conversation_id`
4. **Update Task**: Modify task only if owned by authenticated user
5. **Delete Task**: Remove task only if owned by authenticated user

## Privacy & Security
1. **Data Isolation**: Foreign key constraints ensure data isolation at database level
2. **Audit Trail**: Created/updated timestamps for all entities
3. **Soft Deletes**: Consider implementing soft deletes for conversations/messages for compliance