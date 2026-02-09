# MCP Tools Contract: Phase 5 Part A – Intermediate & Advanced Features

**Feature**: Phase 5 Part A – Intermediate & Advanced Todo Features
**Branch**: `003-intermediate-advanced-features`
**Date**: 2026-02-09

---

## Overview

This document defines the MCP tool signatures and behavior for Phase 5 Part A. All tools extend the existing Phase 3 MCP tools with new fields for priorities, tags, due dates, recurrence, and reminders.

**File**: `backend/mcp/tools.py`

---

## Tool 1: `add_task`

### Signature

```python
@tool
def add_task(
    title: str,
    description: str | None = None,
    priority: str = "medium",
    tags: list[str] | None = None,
    due_date: str | None = None,
    recurrence_rule: str | None = None,
    reminder_offset: int | None = None,
) -> Task:
    """
    Create a new task with optional priority, tags, due date, recurrence, and reminder.

    Args:
        title (str): Task title (required)
        description (str | None): Detailed task description
        priority (str): Priority level: "low", "medium", "high" (default: "medium")
        tags (list[str] | None): User-defined tags for organization (e.g., ["work", "urgent"])
        due_date (str | None): Due date in ISO 8601 format (UTC). Example: "2026-02-15T15:00:00Z"
        recurrence_rule (str | None): Recurrence pattern.
            Formats:
            - "daily" - repeats every day
            - "weekly:monday" or "weekly:mon,wed,fri" - specific days of week
            - "monthly:15" - specific day of month
            - "monthly:last" - last day of month
            - "yearly:march-15" - specific date
            - "custom:every-3-days" - custom interval
        reminder_offset (int | None): Hours before due_date to trigger reminder.
            Example: 24 = remind 1 day before

    Returns:
        Task: The created task object with all fields

    Raises:
        ValueError: If priority not in ["low", "medium", "high"]
        ValueError: If more than 20 tags
        ValueError: If due_date is in the past
        ValueError: If recurrence_rule format invalid
        ValueError: If reminder_offset is negative or > 10080 (7 days)

    Examples:
        >>> add_task(title="Buy milk", priority="high", due_date="2026-02-15T15:00:00Z")
        Task(id=..., title="Buy milk", priority="high", due_date=..., ...)

        >>> add_task(
        ...     title="Weekly review",
        ...     tags=["work", "management"],
        ...     recurrence_rule="weekly:friday",
        ...     reminder_offset=24
        ... )
        Task(id=..., title="Weekly review", recurrence_rule="weekly:friday", ...)
    """
```

### Behavior

1. **Validation**:
   - title: non-empty string (1-255 chars)
   - priority: one of "low", "medium", "high"
   - tags: array of 1-50 char strings, max 20 tags
   - due_date: ISO 8601 datetime in UTC, must be >= now (no past dates)
   - recurrence_rule: matches one of the formats above
   - reminder_offset: non-negative integer, max 10080 hours (7 days)

2. **Behavior**:
   - Creates task with user_id from context (authenticated user)
   - All fields except title are optional with safe defaults
   - Tags array defaults to [] if not provided
   - Priority defaults to "medium"
   - Stores all datetimes in UTC
   - Returns full Task object with generated id, created_at, updated_at

3. **Error Handling**:
   - Return 400 with descriptive error message for validation failures
   - Example: `{"error": "Priority must be one of: low, medium, high"}`

---

## Tool 2: `update_task`

### Signature

```python
@tool
def update_task(
    task_id: str,
    title: str | None = None,
    description: str | None = None,
    status: str | None = None,
    priority: str | None = None,
    tags: list[str] | None = None,
    due_date: str | None = None,
    recurrence_rule: str | None = None,
    reminder_offset: int | None = None,
) -> Task | dict:
    """
    Update task fields (all fields optional).

    Args:
        task_id (str): UUID of task to update
        title (str | None): New title (if omitted, unchanged)
        description (str | None): New description
        status (str | None): "pending" or "completed"
        priority (str | None): "low", "medium", or "high"
        tags (list[str] | None): Updated tags list
        due_date (str | None): Updated due date (ISO 8601 UTC)
        recurrence_rule (str | None): Updated recurrence pattern
        reminder_offset (int | None): Updated reminder offset

    Returns:
        Task: Updated task object (for non-recurring task marked complete)
        dict: {"completed_task": Task, "next_instance": Task} for recurring task marked complete

    Raises:
        ValueError: Task not found
        ValueError: Task belongs to different user (permission denied)
        ValueError: Invalid status transition
        ValueError: Invalid field values (same as add_task)

    Examples:
        >>> update_task(task_id="...", priority="high")
        Task(id=..., priority="high", ...)

        >>> update_task(task_id="...", status="completed")
        # For recurring task, returns both completed task and next instance
        {
            "completed_task": Task(..., status="completed", ...),
            "next_instance": Task(..., status="pending", due_date=tomorrow, ...)
        }
    """
```

### Behavior

1. **PATCH Semantics**:
   - All fields optional
   - Omitted fields retain current value
   - Partial updates supported

2. **Recurring Task Handling**:
   - If status updated to "completed" AND recurrence_rule is set:
     - Mark current task as completed
     - **Immediately** auto-create next instance with:
       - Same title, description, priority, tags, recurrence_rule, reminder_offset
       - New due_date calculated from recurrence pattern
       - Status = "pending"
     - Return dict with both tasks (completed + next instance)
   - If status updated to "completed" AND no recurrence_rule:
     - Just mark as completed, return updated task

3. **Validation**:
   - Same rules as add_task for individual fields
   - Status must be in ["pending", "completed"]
   - Cannot move task to past due date

4. **User Isolation**:
   - Verify task belongs to authenticated user
   - Raise error if user tries to update another user's task

---

## Tool 3: `list_tasks`

### Signature

```python
@tool
def list_tasks(
    priority: str | None = None,
    tags: list[str] | None = None,
    search: str | None = None,
    status: str = "pending",
    sort_by: str = "created_at",
    page: int = 1,
    page_size: int = 20,
) -> dict:
    """
    List tasks with optional filters and sorting.

    Args:
        priority (str | None): Filter by priority ("low", "medium", "high")
        tags (list[str] | None): Filter by tags (list of tag names).
            If provided, returns tasks matching ANY tag (OR logic for chatbot flexibility)
        search (str | None): Full-text search on title and description (case-insensitive)
        status (str): Filter by status ("pending" or "completed", default: "pending")
        sort_by (str): Sort field: "created_at", "-created_at", "due_date", "-due_date",
            "priority", "-priority", "title", "-title"
            (- prefix = descending order)
        page (int): Page number for pagination (default: 1)
        page_size (int): Items per page (default: 20, max: 100)

    Returns:
        dict: {"items": [Task], "total": int, "page": int, "page_size": int}

    Raises:
        ValueError: Invalid filter values

    Examples:
        >>> list_tasks(priority="high")
        {"items": [Task, Task], "total": 2, "page": 1, "page_size": 20}

        >>> list_tasks(priority="high", tags=["work"], status="pending", sort_by="-due_date")
        # Returns high-priority pending work tasks, sorted by due date (most urgent first)

        >>> list_tasks(search="budget")
        # Returns all tasks with "budget" in title or description

        >>> list_tasks(status="pending", sort_by="-due_date")
        # Returns all pending tasks sorted by due date (overdue first)
    """
```

### Behavior

1. **Filtering**:
   - priority: exact match on priority field (optional)
   - tags: if provided, returns tasks with ANY tag in the list (OR logic; more flexible for chatbot)
   - search: case-insensitive substring match on title and description
   - status: exact match on status field (default: "pending")
   - All filters applied: results must match ALL criteria (AND logic)

   **Filter Logic Example**:
   ```
   priority="high" AND tags=["work", "urgent"] AND search="budget"

   Returns tasks matching:
   - priority == "high" AND
   - (tags contains "work" OR tags contains "urgent") AND
   - (title contains "budget" OR description contains "budget")
   ```

2. **Sorting**:
   - Default: sort_by="created_at" (ascending, oldest first)
   - Descending: use "-" prefix (e.g., "-due_date" = newest first)
   - Sorting by priority orders: high > medium > low (for ascending)

3. **Pagination**:
   - Returns paginated results
   - total = total matching items (across all pages)
   - Supports offset = (page - 1) * page_size

4. **User Isolation**:
   - Always filters by authenticated user's user_id
   - Results only include tasks belonging to current user

5. **Overdue Calculation**:
   - Tasks with due_date < now and status="pending" can be requested with status filter
   - Or special status value "overdue" (chatbot convenience)

---

## Tool 4: `complete_task`

### Signature

```python
@tool
def complete_task(task_id: str) -> Task | dict:
    """
    Mark a task as completed. Shorthand for update_task(task_id, status="completed").

    Args:
        task_id (str): UUID of task to complete

    Returns:
        Task: Completed task (if non-recurring)
        dict: {"completed_task": Task, "next_instance": Task} (if recurring)

    Raises:
        ValueError: Task not found
        ValueError: Already completed
    """
```

### Behavior

- Equivalent to `update_task(task_id, status="completed")`
- If task is recurring, auto-creates next instance
- Sets completed_at = now

---

## Tool 5: `delete_task`

### Signature

```python
@tool
def delete_task(task_id: str) -> dict:
    """
    Delete a task (and cancel future recurring instances if recurring).

    Args:
        task_id (str): UUID of task to delete

    Returns:
        dict: {"deleted": true, "id": task_id}

    Raises:
        ValueError: Task not found
        ValueError: User permission denied
    """
```

### Behavior

- Soft delete (mark as deleted) or hard delete (remove from DB) — implementation choice
- If task is recurring, no future instances are created
- User isolation: only owner can delete

---

## Chatbot Intent Mapping

### Intent: set_priority

**Trigger Phrases**:
- "Add a high priority task..."
- "Make this task urgent"
- "Mark as low priority"

**Mapping**:
```python
{
    "urgent" | "important" | "critical" → priority="high",
    "medium" | "normal" → priority="medium",
    "low" | "backlog" → priority="low"
}
```

**Example**:
```
User: "Add high priority task buy milk"
→ add_task(title="buy milk", priority="high")
```

### Intent: add_tags

**Trigger Phrases**:
- "Tag this work"
- "Mark as personal and urgent"
- "Add work and learning tags"

**Mapping**:
```python
{
    "work" → tags=["work"],
    "personal" → tags=["personal"],
    "urgent" → tags=["urgent"],
    "learning" → tags=["learning"],
    # Multiple tags: combine above
}
```

**Example**:
```
User: "Tag as work and urgent"
→ update_task(task_id, tags=["work", "urgent"])
```

### Intent: set_due_date

**Trigger Phrases**:
- "Due tomorrow"
- "Due Friday at 3pm"
- "Due next Monday"
- "Deadline is February 15"

**Mapping**:
```python
{
    "tomorrow" → due_date = tomorrow at 00:00 UTC,
    "next Friday" → due_date = next Friday at 00:00 UTC,
    "[DATE] at [TIME]" → due_date = parsed datetime UTC,
    # Natural date parsing required
}
```

**Example**:
```
User: "Due Friday at 3pm"
→ due_date = next Friday at 15:00 UTC (converted to user's timezone on display)
```

### Intent: set_recurrence

**Trigger Phrases**:
- "Repeat daily"
- "Weekly on Monday"
- "Every month on the 15th"
- "Yearly on March 15"

**Mapping**:
```python
{
    "daily" → recurrence_rule="daily",
    "weekly on [DAY]" → recurrence_rule=f"weekly:{day}",
    "monthly on [DAY]" → recurrence_rule=f"monthly:{day}",
    "yearly on [DATE]" → recurrence_rule=f"yearly:{month}-{day}",
}
```

**Example**:
```
User: "Make this weekly on Monday"
→ update_task(task_id, recurrence_rule="weekly:monday")
```

### Intent: set_reminder

**Trigger Phrases**:
- "Remind me 1 day before"
- "Remind me 1 hour before"
- "Reminder 2 days before"

**Mapping**:
```python
{
    "[N] day[s] before" → reminder_offset = N * 24 (hours),
    "[N] hour[s] before" → reminder_offset = N,
    "1 week before" → reminder_offset = 7 * 24,
}
```

**Example**:
```
User: "Remind me 1 day before"
→ update_task(task_id, reminder_offset=24)
```

### Intent: filter_and_search

**Trigger Phrases**:
- "Show high priority tasks"
- "Show pending work tasks"
- "Search for budget"
- "Find tasks due tomorrow"

**Mapping**:
```python
list_tasks(
    priority=extract_priority(user_input),
    tags=extract_tags(user_input),
    search=extract_search_term(user_input),
    status=extract_status(user_input),
    sort_by=extract_sort(user_input)
)
```

**Example**:
```
User: "Show pending high priority work tasks"
→ list_tasks(priority="high", tags=["work"], status="pending")
```

---

## Error Handling

### Tool Errors

All tools should return descriptive error messages:

```json
{
    "error": "Invalid priority. Must be one of: low, medium, high",
    "error_code": "INVALID_PRIORITY",
    "details": null
}
```

### Validation Errors

| Field | Validation | Error |
|-------|-----------|-------|
| priority | not in ["low", "medium", "high"] | INVALID_PRIORITY |
| tags | more than 20 | TOO_MANY_TAGS |
| tags | empty strings | INVALID_TAG_FORMAT |
| due_date | in past | DUE_DATE_IN_PAST |
| due_date | invalid format | INVALID_DATETIME_FORMAT |
| recurrence_rule | invalid pattern | INVALID_RECURRENCE_PATTERN |
| reminder_offset | negative | INVALID_REMINDER_OFFSET |
| reminder_offset | > 10080 | REMINDER_OFFSET_TOO_LARGE |
| task_id | not found | TASK_NOT_FOUND |
| user permission | different user owns task | PERMISSION_DENIED |

---

## Implementation Checklist

- [ ] Extend Task model with 5 new fields (priority, tags, due_date, recurrence_rule, reminder_offset)
- [ ] Update add_task signature and validation
- [ ] Update update_task signature and recurring task logic
- [ ] Update list_tasks signature with new filter params
- [ ] Add complete_task shorthand
- [ ] Add delete_task tool
- [ ] Implement recurring task auto-creation (on update to status="completed")
- [ ] Add error handling with descriptive messages
- [ ] Document all tool changes
- [ ] Test all tools with pytest
- [ ] Verify user isolation (user_id filtering)

