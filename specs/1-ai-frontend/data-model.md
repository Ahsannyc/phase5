# Data Model: AI-Themed Todo Frontend

## Overview
This document defines the data structures and entities used in the AI-themed Todo frontend application. The data model supports the core functionality of the multi-user todo application while maintaining consistency with the futuristic AI aesthetic.

## Core Entities

### Task Entity
The Task entity represents a single todo item in the system.

**Fields:**
- `id`: number (required) - Unique identifier for the task
- `title`: string (required) - The main title/description of the task
- `description`: string (optional) - Extended details about the task
- `completed`: boolean (required) - Whether the task is completed or not
- `createdAt`: string (required) - ISO date string representing when the task was created
- `updatedAt`: string (required) - ISO date string representing when the task was last updated

**Validation Rules:**
- `id` must be a positive integer
- `title` must be a non-empty string (1-200 characters)
- `description` can be empty or up to 1000 characters
- `completed` defaults to false
- `createdAt` and `updatedAt` must be valid ISO 8601 date strings

**State Transitions:**
- `pending` → `completed` when task is marked complete
- `completed` → `pending` when task is marked incomplete

**Sample Object:**
```json
{
  "id": 123,
  "title": "Implement AI-themed dashboard",
  "description": "Create the main dashboard with glassmorphism effects",
  "completed": false,
  "createdAt": "2025-12-15T10:30:00Z",
  "updatedAt": "2025-12-15T10:30:00Z"
}
```

### TaskCreateInput Entity
Represents the data required to create a new task.

**Fields:**
- `title`: string (required) - The main title/description of the task
- `description`: string (optional) - Extended details about the task

**Validation Rules:**
- `title` must be a non-empty string (1-200 characters)
- `description` is optional, can be up to 1000 characters
- At least one field must be provided

**Sample Object:**
```json
{
  "title": "Add task completion toggle",
  "description": "Implement the checkbox functionality for marking tasks as complete"
}
```

### TaskUpdateInput Entity
Represents the data required to update an existing task.

**Fields:**
- `title`: string (optional) - The new title for the task
- `description`: string (optional) - The new description for the task
- `completed`: boolean (optional) - The new completion status

**Validation Rules:**
- At least one field must be provided
- If `title` is provided, it must be a non-empty string (1-200 characters)
- If `description` is provided, it can be up to 1000 characters
- If `completed` is provided, it must be a boolean value

**Sample Object:**
```json
{
  "title": "Enhanced task completion toggle",
  "completed": true
}
```

### User Entity (External Reference)
Represents the user in the system. This entity is managed by the authentication system and referenced by tasks.

**Fields:**
- `id`: number (required) - Unique identifier for the user
- `email`: string (required) - User's email address
- `name`: string (optional) - User's display name
- `createdAt`: string (required) - When the user account was created

**Relationships:**
- Each user can have many tasks
- Tasks are linked to users via the `userId` field

## API Response Structures

### Task List Response
Response for fetching multiple tasks.

**Structure:**
- `tasks`: Task[] (required) - Array of task objects

**Sample Response:**
```json
{
  "tasks": [
    {
      "id": 1,
      "title": "First task",
      "description": "Description of first task",
      "completed": false,
      "createdAt": "2025-12-15T10:00:00Z",
      "updatedAt": "2025-12-15T10:00:00Z"
    },
    {
      "id": 2,
      "title": "Second task",
      "description": "Description of second task",
      "completed": true,
      "createdAt": "2025-12-15T10:15:00Z",
      "updatedAt": "2025-12-15T10:45:00Z"
    }
  ]
}
```

### Single Task Response
Response for fetching a single task.

**Structure:**
- `task`: Task (required) - The requested task object
- `error`: string (optional) - Error message if request failed

**Sample Response:**
```json
{
  "task": {
    "id": 1,
    "title": "Single task",
    "description": "Description of the task",
    "completed": false,
    "createdAt": "2025-12-15T10:00:00Z",
    "updatedAt": "2025-12-15T10:00:00Z"
  }
}
```

### Operation Result Response
Standard response structure for create, update, and delete operations.

**Structure:**
- `success`: boolean (required) - Whether the operation succeeded
- `task`: Task (optional) - The resulting task object if successful
- `error`: string (optional) - Error message if operation failed

**Sample Response:**
```json
{
  "success": true,
  "task": {
    "id": 123,
    "title": "New task",
    "description": "Description of new task",
    "completed": false,
    "createdAt": "2025-12-15T10:30:00Z",
    "updatedAt": "2025-12-15T10:30:00Z"
  }
}
```

## State Management Objects

### Task State
Represents the state of tasks in the frontend application.

**Structure:**
- `loading`: boolean (required) - Whether tasks are currently being loaded
- `tasks`: Task[] (required) - Current list of tasks
- `error`: string (optional) - Error message if there was a problem
- `currentFilter`: string (optional) - Current filter applied to the task list

**Sample Object:**
```json
{
  "loading": false,
  "tasks": [
    // Array of Task objects
  ],
  "error": null,
  "currentFilter": "all"
}
```

### Form State
Represents the state of task creation/editing forms.

**Structure:**
- `title`: string (required) - Current value of title field
- `description`: string (required) - Current value of description field
- `submitting`: boolean (required) - Whether form is currently submitting
- `error`: string (optional) - Error message if there was a problem

**Sample Object:**
```json
{
  "title": "New task title",
  "description": "New task description",
  "submitting": false,
  "error": null
}
```

## Relationships

### Task to User Relationship
- Each Task belongs to exactly one User
- Implemented via `userId` field in the Task entity (external reference)
- Frontend ensures user isolation by only displaying tasks with matching userId

### Task to Task Relationships
- No direct relationships between tasks
- Tasks are organized by user and filtered by completion status
- Tasks are sorted by creation date or other criteria in the UI

## Validation Summary

### Client-Side Validation
- Title length: 1-200 characters
- Description length: 0-1000 characters
- Required fields presence
- Data type validation (boolean, string, number)
- Format validation (ISO date strings)

### Error States
- Invalid input: Show specific error messages
- Network errors: Show connectivity issues
- Authentication errors: Redirect to login
- Authorization errors: Show permission denied

## UI State Mapping

### Task Card Display
- Display title prominently
- Show description if available
- Visual indication of completion status
- Timestamps for creation/update
- Interactive elements for modification

### Task Form Display
- Input fields for title and description
- Checkbox for completion status
- Submit/cancel buttons
- Loading states during submission
- Error messaging for validation failures