# Data Model: Todo AI Chatbot

## Entities

### Conversation
- id: integer (primary key)
- user_id: integer (foreign key to users.id)
- created_at: datetime (timestamp)
- updated_at: datetime (timestamp)
- Relationships: belongs to User, has many Messages

### Message
- id: integer (primary key)
- conversation_id: integer (foreign key to conversations.id)
- user_id: integer (foreign key to users.id)
- role: string (enum: 'user' or 'assistant')
- content: string (text content of the message)
- created_at: datetime (timestamp)
- Relationships: belongs to Conversation and User

## Validation Rules

### Conversation
- user_id must exist in users table
- user_id must match authenticated user during creation/modification
- created_at and updated_at automatically set by system

### Message
- conversation_id must exist in conversations table
- user_id must exist in users table
- role must be either 'user' or 'assistant'
- content must not exceed 10,000 characters
- user_id must match authenticated user during creation

## State Transitions

### Conversation
- Created when user initiates first chat in a session
- Updated when new messages are added
- Remains active until user ends session or timeout occurs

### Message
- Created when user sends message or system generates response
- Immutable once created (no updates allowed)