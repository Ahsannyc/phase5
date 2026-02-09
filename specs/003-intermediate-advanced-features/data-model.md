# Data Model: Phase 5 Part A – Intermediate & Advanced Features

**Feature**: Phase 5 Part A – Intermediate & Advanced Todo Features
**Branch**: `003-intermediate-advanced-features`
**Date**: 2026-02-09

---

## Overview

This document defines the data model extensions for Phase 5 Part A. All changes are additive to the existing Phase 2 Task model. No new tables are required.

---

## Entity: Task (Extended)

**Table**: `task` (existing, adding 5 new columns)
**File**: `backend/app/models/task.py`

### Fields

#### Existing Fields (Phase 1-2)
| Field | Type | Nullable | Default | Notes |
|-------|------|----------|---------|-------|
| `id` | UUID | NO | uuid4() | Primary key |
| `user_id` | UUID | NO | — | Foreign key to `user.id` |
| `title` | str | NO | — | Task title |
| `description` | str | YES | NULL | Task description |
| `status` | str | NO | "pending" | PENDING or COMPLETED |
| `created_at` | datetime | NO | utcnow() | UTC timestamp |
| `updated_at` | datetime | NO | utcnow() | UTC timestamp |
| `completed_at` | datetime | YES | NULL | When marked complete |

#### New Fields (Phase 5 Part A)

**Intermediate Features**:
| Field | Type | Nullable | Default | Notes |
|-------|------|----------|---------|-------|
| `priority` | str | NO | "medium" | Enum: "low", "medium", "high" |
| `tags` | list[str] (JSON) | NO | [] | Array of user-defined tags; stored as JSON array |

**Advanced Features**:
| Field | Type | Nullable | Default | Notes |
|-------|------|----------|---------|-------|
| `due_date` | datetime | YES | NULL | Due date in UTC; nullable (optional) |
| `recurrence_rule` | str | YES | NULL | Recurrence pattern; examples: "daily", "weekly:monday", "monthly:15", "yearly:march-15" |
| `reminder_offset` | int | YES | NULL | Hours before due_date to remind user; e.g., 24 = 1 day before |

### Enums

```python
class TaskStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"

class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
```

### Validation Rules

| Field | Validation | Error Message |
|-------|-----------|------|
| `priority` | Must be in ["low", "medium", "high"] | Invalid priority |
| `tags` | Array of non-empty strings; max 20 tags; max 50 chars each | Invalid tags format |
| `due_date` | If set, must be valid ISO 8601 datetime; should be >= now | Invalid due date |
| `recurrence_rule` | If set, must match pattern: daily/weekly/monthly/yearly:day/custom:pattern | Invalid recurrence rule |
| `reminder_offset` | If set, must be integer >= 0; reasonable max 10080 (7 days) | Invalid reminder offset |

### Indexes

**Performance indexes** (Alembic migration):

```sql
CREATE INDEX idx_task_priority ON task(priority);
CREATE INDEX idx_task_due_date ON task(due_date);
CREATE INDEX idx_task_recurrence_rule ON task(recurrence_rule);
CREATE INDEX idx_task_tags ON task USING GIN(tags);  -- PostgreSQL GIN index for JSON array
CREATE INDEX idx_task_user_status ON task(user_id, status);  -- Composite for scoped queries
```

---

## State Transitions

### Task Lifecycle with Recurring Tasks

```
[New Task Created]
        |
        v
[PENDING] -- (complete) --> [COMPLETED]
        ^
        |
   (if recurring & completed)
        |
   [Auto-create next instance]
        |
   (new PENDING task with updated due_date)
```

**Key behavior**:
- When a recurring task is marked COMPLETED, backend auto-creates a new instance with recurrence_rule applied
- Next instance inherits: title, description, priority, tags, recurrence_rule, reminder_offset
- Next instance's due_date is calculated from current due_date + recurrence interval
- Next instance status = PENDING

### Reminder State

**Reminders are stored as `reminder_offset` integer; not a separate table.**

- On task creation/update: if `reminder_offset` is set, calculate absolute datetime = `due_date - reminder_offset (hours)`
- On task retrieval: use due_date + reminder_offset to determine if reminder should be triggered
- No scheduler/background job needed for Phase 5 Part A; reminders are calculated on-demand
- Future: Part B/C can add background scheduling via Dapr Bindings (cron) or Kafka

---

## Database Schema (SQL)

### Alembic Migration

**File**: `alembic/versions/*_extend_task_intermediate_advanced_features.py`

```sql
-- Add new columns to task table
ALTER TABLE task ADD COLUMN priority VARCHAR(20) NOT NULL DEFAULT 'medium';
ALTER TABLE task ADD COLUMN tags JSONB NOT NULL DEFAULT '[]';
ALTER TABLE task ADD COLUMN due_date TIMESTAMP NULL;
ALTER TABLE task ADD COLUMN recurrence_rule VARCHAR(255) NULL;
ALTER TABLE task ADD COLUMN reminder_offset INTEGER NULL;

-- Add indexes
CREATE INDEX idx_task_priority ON task(priority);
CREATE INDEX idx_task_due_date ON task(due_date);
CREATE INDEX idx_task_recurrence_rule ON task(recurrence_rule);
CREATE INDEX idx_task_tags ON task USING GIN(tags);
CREATE INDEX idx_task_user_status ON task(user_id, status);

-- Add NOT NULL constraint with default for backward compatibility
ALTER TABLE task ALTER COLUMN tags SET DEFAULT '[]';
ALTER TABLE task ALTER COLUMN priority SET DEFAULT 'medium';
```

### SQLModel Definition

```python
from typing import Optional
from datetime import datetime
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import JSON
from enum import Enum

class TaskStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"

class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class Task(SQLModel, table=True):
    # Existing fields
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", index=True)
    title: str = Field(index=True)
    description: Optional[str] = None
    status: TaskStatus = Field(default=TaskStatus.PENDING, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

    # NEW FIELDS - Intermediate Features
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM, index=True)
    tags: list[str] = Field(default=[], sa_column=Column(JSON), index=True)

    # NEW FIELDS - Advanced Features
    due_date: Optional[datetime] = Field(None, index=True)  # UTC timezone
    recurrence_rule: Optional[str] = Field(None, index=True)  # "daily", "weekly:monday", etc.
    reminder_offset: Optional[int] = None  # Hours before due_date

    # Computed properties
    @property
    def is_overdue(self) -> bool:
        """Returns True if due_date is in the past and status is PENDING."""
        if self.due_date and self.status == TaskStatus.PENDING:
            return self.due_date < datetime.utcnow()
        return False

    @property
    def reminder_datetime(self) -> Optional[datetime]:
        """Returns the datetime when reminder should trigger."""
        if self.due_date and self.reminder_offset:
            return self.due_date - timedelta(hours=self.reminder_offset)
        return None
```

---

## Relationships & Dependencies

| Entity | Relationship | Cardinality | Notes |
|--------|-------------|----------|-------|
| Task | Belongs to User | N:1 | Every task has exactly one user (user_id FK) |
| Task | Recurs from Task | Optional 1:1 | A task can have a recurrence_rule; future instances auto-created |
| Task | Has Tags | N:M (denormalized) | Tags stored as JSON array; no separate Tag table for Phase 5 |

**Future Normalization** (Part B/C if needed):
- If tag count grows or performance degradation observed, create `Tag` table and `TaskTag` junction
- Current Phase 5 design is sufficient for MVP

---

## Backward Compatibility

✅ **All new fields are backward compatible**:
- New fields have NOT NULL defaults (priority='medium', tags=[])
- Existing queries still work: no breaking changes to existing columns
- New fields are optional in API (all nullable on update)
- Existing tasks automatically get defaults when migration is applied

---

## Query Patterns

### Find overdue tasks
```sql
SELECT * FROM task
WHERE user_id = $1
  AND status = 'pending'
  AND due_date < NOW()
  AND due_date IS NOT NULL
ORDER BY due_date ASC;
```

### Find tasks by priority
```sql
SELECT * FROM task
WHERE user_id = $1
  AND priority = $2
ORDER BY created_at DESC;
```

### Find tasks by tag
```sql
SELECT * FROM task
WHERE user_id = $1
  AND tags ? $2  -- PostgreSQL JSON contains operator
ORDER BY created_at DESC;
```

### Find recurring tasks
```sql
SELECT * FROM task
WHERE user_id = $1
  AND recurrence_rule IS NOT NULL
ORDER BY created_at DESC;
```

### Combined filter (priority + tag + status)
```sql
SELECT * FROM task
WHERE user_id = $1
  AND status = $2
  AND priority = $3
  AND tags ? $4
ORDER BY due_date ASC;
```

---

## Constraints & Assumptions

| Constraint | Assumption | Rationale |
|-----------|-----------|----------|
| Max 20 tags per task | Users won't create hundreds of tags | Prevents JSON array bloat |
| Recurrence rules are simplified (not full RRULE) | 80% of use cases covered | Full RRULE complexity deferred to Part B/C |
| All datetimes in UTC | Backend stores UTC; frontend converts | Standard pattern; prevents timezone bugs |
| Reminder_offset in hours | Sufficient granularity for MVP | Can add minutes/seconds if needed later |
| Tags are denormalized (JSON array) | Faster reads; acceptable for Phase 5 scale | Can normalize in future if needed |

---

## Migration Strategy

### Phase 0: Schema Design (COMPLETE ✅)
- Columns designed with backward-compatible defaults
- Indexes planned for performance

### Phase 1: Alembic Migration (READY)
- Migration script auto-generated from model
- Applied to Neon PostgreSQL dev database
- Rollback tested (if needed)

### Phase 2: Data Backfill (NOT NEEDED)
- No existing data needs transformation
- All fields have safe defaults
- Existing tasks unaffected

### Phase 3: Deployment (Post-Implementation)
- Migration runs on cloud database
- No downtime expected (additive columns)

---

## Performance Considerations

| Operation | Complexity | Notes |
|-----------|-----------|-------|
| Create task with tags | O(1) | JSON array stored as single value |
| Filter by priority | O(n) | Indexed; <10ms for 10k tasks |
| Filter by tag | O(n) | GIN index on JSON; <10ms for 10k tasks |
| Search by title | O(n) | ILIKE; <500ms for 10k tasks; can upgrade to FTS later |
| Sort by due_date | O(n log n) | Indexed; <500ms for 10k tasks |
| Recurring task auto-create | O(1) | On completion; minimal overhead |
| Retrieve task with all fields | O(1) | No joins required |

**Scalability**: Current design suitable for 100k+ tasks per user before optimization needed.

---

## Validation & Testing

### Unit Tests (for each field)
- `priority`: accepts low/medium/high; rejects invalid values
- `tags`: accepts array of strings; rejects non-string values; enforces max 20 tags
- `due_date`: accepts ISO 8601; rejects invalid dates; is_overdue computed correctly
- `recurrence_rule`: accepts valid patterns; rejects invalid patterns
- `reminder_offset`: accepts non-negative integers; rejects negative values

### Integration Tests (for queries)
- Filter by priority returns only matching tasks
- Filter by tag returns only matching tasks (exact match)
- Combined filters (priority + tag) return only matching ALL criteria
- Sort by due_date orders correctly (ascending/descending)
- Overdue query returns only past-due incomplete tasks
- User isolation: query with one user_id doesn't return another user's tasks

### End-to-End Tests
- Create task via API with all new fields → persists correctly
- Retrieve task → all fields returned correctly
- Update task (change priority/tags) → update reflected immediately
- Mark recurring task complete → next instance auto-created with correct due_date
- Filter via API → correct subset returned

