# Data Model: Backend Todo Application

## Overview
This document defines the database entities and relationships for the multi-user Todo application backend using SQLModel. The data model supports the core functionality of the todo application while maintaining proper user isolation and security requirements.

## Core Entities

### User Entity
The User entity represents a registered user in the system.

**Fields:**
- `id`: int (primary key, auto-increment) - Unique identifier for the user
- `email`: str (unique, indexed) - User's email address for authentication
- `password_hash`: str - Hashed password using bcrypt or argon2
- `name`: str (optional) - User's display name
- `created_at`: datetime (default now) - When the user account was created

**Constraints:**
- `email` must be unique
- `email` must be a valid email format
- `password_hash` must meet security requirements

**Indexing:**
- Primary key index on `id`
- Unique index on `email`

**Relationships:**
- One User to Many Tasks (via foreign key `tasks.user_id`)

**Sample Object:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "name": "John Doe",
  "created_at": "2026-02-05T12:00:00Z"
}
```

### Task Entity
The Task entity represents a single todo item owned by a specific user.

**Fields:**
- `id`: int (primary key, auto-increment) - Unique identifier for the task
- `user_id`: int (foreign key to users.id, indexed) - Owner of the task
- `title`: str - Title/description of the task
- `description`: str (optional) - Extended details about the task
- `completed`: bool (default False) - Whether the task is completed
- `created_at`: datetime (default now) - When the task was created
- `updated_at`: datetime (default now, updates on modification) - When the task was last updated

**Constraints:**
- `title` must not be empty
- `user_id` must reference a valid user
- `completed` defaults to False

**Indexing:**
- Primary key index on `id`
- Index on `user_id` for efficient filtering
- Index on `completed` for status-based queries
- Composite index on `(user_id, completed)` for common queries

**State Transitions:**
- `pending` → `completed` when task is marked complete
- `completed` → `pending` when task is marked incomplete

**Sample Object:**
```json
{
  "id": 123,
  "user_id": 1,
  "title": "Implement authentication system",
  "description": "Build a secure JWT-based auth system",
  "completed": false,
  "created_at": "2026-02-05T10:30:00Z",
  "updated_at": "2026-02-05T10:30:00Z"
}
```

## API Request/Response Objects

### Authentication Objects

**Signup Request**
- `email`: str - User's email address
- `password`: str - Plain text password (will be hashed)
- `name`: str (optional) - User's display name

**Signup Response**
- `user`: User object (without password_hash)
- `token`: str - JWT token for authentication

**Signin Request**
- `email`: str - User's email address
- `password`: str - Plain text password

**Signin Response**
- `user`: User object (without password_hash)
- `token`: str - JWT token for authentication

### Task Objects

**Task Creation Request**
- `title`: str - Title of the task (required)
- `description`: str (optional) - Extended details about the task

**Task Update Request**
- `title`: str (optional) - New title for the task
- `description`: str (optional) - New description for the task

**Task Completion Toggle Request**
- `completed`: bool - New completion status

**Task Response (Full)**
- `id`: int - Task identifier
- `user_id`: int - Owner identifier
- `title`: str - Task title
- `description`: str (optional) - Task description
- `completed`: bool - Completion status
- `created_at`: datetime - Creation timestamp
- `updated_at`: datetime - Last update timestamp

## Database Relationships

### User to Tasks
- **Relationship**: One-to-Many (One user can have many tasks)
- **Implementation**: Foreign key from `tasks.user_id` to `users.id`
- **Constraint**: ON DELETE CASCADE (deleting a user deletes their tasks)
- **Query Pattern**: `SELECT * FROM tasks WHERE user_id = $user_id`

## Validation Rules

### User Validation
- Email format validation using regex
- Email uniqueness enforcement at database level
- Password strength validation (minimum length, complexity)
- Name length limits (e.g., max 100 characters)

### Task Validation
- Title required and non-empty (min 1 character)
- Title length limits (e.g., max 200 characters)
- Description length limits (e.g., max 1000 characters)
- User_id must reference an existing user
- User_id ownership validation for all operations

## Security Considerations

### Data Isolation
- All task queries must be filtered by `user_id`
- Cross-user access prevention at both application and database levels
- Authorization checks in every task-related endpoint

### Password Security
- Passwords must be hashed using bcrypt or argon2
- No plain-text passwords stored in the database
- Secure password hashing parameters

### Audit Trail
- Track creation and modification timestamps
- Consider adding a field for who made changes in future versions

## Performance Optimizations

### Indexing Strategy
- Primary indexes on all primary keys
- Foreign key indexes on relationship fields
- Composite indexes for common query patterns (user_id + completed)
- Consider partial indexes for frequently queried subsets

### Query Optimization
- Always filter by user_id for task queries
- Use LIMIT/OFFSET for pagination
- Consider read replicas for heavy read operations

## Schema Evolution

### Versioning Strategy
- Use Alembic for migration management
- Document breaking changes
- Maintain backward compatibility when possible

### Change Management
- All schema changes must have corresponding migration scripts
- Test migrations in development before production
- Plan for zero-downtime deployments where possible