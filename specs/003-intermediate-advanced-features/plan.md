# Implementation Plan: Phase 5 Part A – Intermediate & Advanced Features

**Branch**: `003-intermediate-advanced-features` | **Date**: 2026-02-08 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/003-intermediate-advanced-features/spec.md`

## Summary

Extend the existing Phase 2-3 Todo application (Next.js frontend + FastAPI backend + AI chatbot) with Intermediate features (Priorities, Tags, Search, Filter, Sort) and Advanced features (Recurring Tasks, Due Dates & Reminders). All features integrate seamlessly with the web UI and AI chatbot. No new frameworks or external dependencies required; only extensions to existing models, APIs, and MCP tools.

---

## Technical Context

**Language/Version**: Python 3.11-3.12 (backend), Node.js 20+ (frontend)
**Primary Dependencies**: FastAPI, SQLModel, Next.js, TypeScript, Tailwind CSS, Better Auth, OpenAI Agents SDK, Cohere API
**Storage**: Neon PostgreSQL (external, existing from Phase 2)
**Testing**: Unit tests for backend models/routes, integration tests for API, component tests for frontend
**Target Platform**: Existing Phase 2-3 stack (no changes to deployment, only feature additions)
**Project Type**: Web application with chatbot integration
**Performance Goals**: Search <1s, filter <500ms, recurring task creation <5s, multi-filter operations <1s
**Constraints**: No new external libraries, no breaking changes to Phase 2-3 APIs, backward-compatible schema, stateless backend
**Scale/Scope**: Extend existing Task model with 5 new fields; update 2 API routes (POST/PUT, GET with filters); extend 2 MCP tools; update 4 frontend components

---

## Constitution Check

**GATE: Must pass before Phase 0 research.**

| Principle | Requirement | Status | Notes |
|-----------|-------------|--------|-------|
| Spec-Driven Development | Spec exists and approved | ✅ PASS | `/specs/003-intermediate-advanced-features/spec.md` complete and validated |
| Agent Boundaries | Clear agent roles for implementation | ✅ PASS | Database Engineer (schema), Backend Engineer (routes), MCP Engineer (tools), AI Agent Engineer (prompts), Frontend Engineer (UI), ChatKit Frontend Agent (chatbot UI) |
| Backward Compatibility | No breaking changes to Phase 2-3 | ✅ PASS | All fields additive to Task model; existing API endpoints extended, not changed |
| Multi-User Isolation | user_id enforcement | ✅ PASS | All new queries/filters enforce user_id filtering; authentication unchanged |
| No New Dependencies | Only extend existing stack | ✅ PASS | No new libraries; using SQLModel, FastAPI, Next.js, Tailwind as-is |
| Chatbot Integration | MCP tools extend existing pattern | ✅ PASS | New/updated MCP tools follow existing pattern from Phase 3 |
| Constitution Alignment | Phase 5 Part A requirements met | ✅ PASS | Spec implements all Intermediate + Advanced features; chatbot integration explicit |

**Gate Result**: ✅ **PASS** – All constitution principles satisfied. Proceed to Phase 0.

---

## Phase 0: Research & Decision Documentation

### Research Tasks

1. **Priority Field Implementation** (database)
   - **Question**: Use enum (low/medium/high) or numeric scale (1-5)?
   - **Decision**: Enum (low, medium, high) — more semantic, easier for chatbot NLP, aligns with UI
   - **Rationale**: User stories use human-readable priorities; easier to map from natural language ("high priority" → priority="high")
   - **Alternatives considered**: Numeric scale (more flexible but less semantic for chatbot); boolean flags (insufficient granularity)

2. **Tag Storage** (database)
   - **Question**: Normalized table (Tag + TaskTag junction) or JSON array in Task?
   - **Decision**: JSON array in Task (tags: list[str]) — simpler for MVP, sufficient for user count at Phase 5
   - **Rationale**: Avoids join queries; tags are ephemeral and user-defined; simple array sufficient for now
   - **Alternatives considered**: Normalized schema (better for scale but adds complexity); JSONB with GIN index (overkill for Phase 5)
   - **Migration path**: Can normalize to proper schema in future phase if needed

3. **Recurrence Rule Format** (database)
   - **Question**: Use RRULE format (RFC 5545) or simplified strings ("daily", "weekly:monday")?
   - **Decision**: Simplified strings initially, RRULE support added later — simpler for MVP, sufficient for 80% of use cases
   - **Rationale**: Easier to parse in chatbot NLP; human-readable in database; can extend with RRULE later
   - **Alternatives considered**: Full RRULE (more powerful but harder to parse); custom DSL (proprietary, harder to debug)
   - **Example**: "daily", "weekly:monday", "monthly:15", "yearly:march-15", "custom:every-3-days"

4. **Due Date & Reminder Storage** (database)
   - **Question**: Store reminder as absolute datetime or as offset from due_date?
   - **Decision**: Store reminder_offset as integer (hours/days) — calculate absolute datetime on demand
   - **Rationale**: Offset survives timezone changes; simpler to adjust; due_date is source of truth
   - **Alternatives considered**: Absolute datetime (brittle across timezones); relative descriptions (harder to query)

5. **Search Implementation** (backend)
   - **Question**: Use PostgreSQL full-text search (FTS) or simple LIKE/ILIKE?
   - **Decision**: ILIKE for MVP (simple, sufficient for Phase 5); FTS (trigram GIN) in future phase if needed
   - **Rationale**: 80/20 rule — ILIKE covers most searches; FTS adds complexity; can optimize later
   - **Alternatives considered**: Full-text search (better relevance but more setup); regex (slower)

6. **Filter Combination Logic** (backend)
   - **Question**: Should multiple filters combine with AND or OR?
   - **Decision**: AND for all criteria (status AND priority AND tag) — more intuitive for users
   - **Rationale**: "Show pending high-priority work tasks" means all criteria must match; more predictable behavior
   - **Alternatives considered**: OR (less predictable); configurable (adds complexity)

7. **Recurring Task Auto-Creation** (backend)
   - **Question**: Should next instance auto-create on completion or on schedule?
   - **Decision**: Auto-create on completion — simpler, more user-friendly
   - **Rationale**: User expects task to disappear and reappear when marked complete; no background job needed
   - **Alternatives considered**: Scheduled creation (needs async worker, more complex); manual creation (doesn't feel automatic)

8. **Timezone Handling** (backend + frontend)
   - **Question**: How to handle user timezone across frontend and backend?
   - **Decision**: Store all datetimes in UTC (backend); display in user's timezone (frontend from browser or user profile)
   - **Rationale**: Standard pattern; prevents ambiguity; user's browser provides timezone
   - **Alternatives considered**: Server stores user timezone (adds complexity); all calculations in UTC (works but less user-friendly)

### Research Output: `research.md`

All decisions above are documented and rationale is clear. No blocking unknowns remain.

**Status**: Phase 0 research complete ✅

---

## Phase 1: Design & Contracts

### Data Model Design

#### Extended Task Model

**File**: `backend/app/models/task.py`

```python
class Task(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id")  # Existing
    title: str  # Existing
    description: str | None = None  # Existing
    status: TaskStatus = Field(default=TaskStatus.PENDING)  # Existing (PENDING, COMPLETED)

    # NEW FIELDS - Intermediate Features
    priority: str = Field(default="medium")  # "low", "medium", "high"
    tags: list[str] = Field(default=[], sa_column=Column(JSON))  # e.g. ["work", "urgent"]

    # NEW FIELDS - Advanced Features
    due_date: datetime | None = None  # UTC timezone
    recurrence_rule: str | None = None  # e.g. "daily", "weekly:monday", "monthly:15"
    reminder_offset: int | None = None  # Hours/days before due_date

    # Existing temporal fields
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None

class TaskStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"

class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
```

**Database Indexes** (Alembic migration):
- `due_date` (for sorting/filtering by due date)
- `priority` (for filtering/sorting)
- `tags` (GIN index on JSON array, for filtering)
- `recurrence_rule` (for finding recurring tasks)
- `user_id, status` (composite, for user-scoped queries)

#### Schema Changes

**Alembic Migration**: `alembic/versions/*_extend_task_with_intermediate_advanced_features.py`

```sql
ALTER TABLE task ADD COLUMN priority VARCHAR DEFAULT 'medium';
ALTER TABLE task ADD COLUMN tags JSONB DEFAULT '[]';
ALTER TABLE task ADD COLUMN due_date TIMESTAMP;
ALTER TABLE task ADD COLUMN recurrence_rule VARCHAR;
ALTER TABLE task ADD COLUMN reminder_offset INTEGER;

CREATE INDEX idx_task_due_date ON task(due_date);
CREATE INDEX idx_task_priority ON task(priority);
CREATE INDEX idx_task_tags ON task USING GIN(tags);
CREATE INDEX idx_task_recurrence_rule ON task(recurrence_rule);
CREATE INDEX idx_task_user_status ON task(user_id, status);
```

**No new tables needed** — all fields fit into existing Task model.

### API Contract Design

#### Extended Endpoints

**POST /api/{user_id}/tasks** (create task)

Request body (extends existing):
```json
{
  "title": "string (required)",
  "description": "string | null",
  "priority": "low | medium | high (default: medium)",
  "tags": ["string"] (default: []),
  "due_date": "ISO 8601 datetime | null",
  "recurrence_rule": "daily | weekly:monday | monthly:15 | null",
  "reminder_offset": "integer (hours) | null"
}
```

Response: `Task` object with all new fields

**PATCH /api/{user_id}/tasks/{task_id}** (update task)

Same request body as POST (all fields optional for PATCH).

**GET /api/{user_id}/tasks** (list tasks with filters)

Query parameters (extend existing):
```
?priority=low|medium|high
?tag=string (can repeat: ?tag=work&tag=urgent)
?search=string (full-text on title/description)
?status=pending|completed|overdue
?due_date_range=today|week|month|overdue
?sort=priority|due_date|created_at|-created_at (- = descending)
```

Response: `List[Task]` filtered, sorted, and paginated

**GET /api/{user_id}/tasks/overdue** (optional convenience endpoint)

Returns tasks with due_date < now and status != COMPLETED

### MCP Tool Contract

**File**: `backend/mcp/tools.py`

Extend existing tools with new fields:

```python
@tool
def add_task(
    title: str,
    description: str | None = None,
    priority: str = "medium",  # NEW
    tags: list[str] | None = None,  # NEW
    due_date: str | None = None,  # NEW (ISO 8601)
    recurrence_rule: str | None = None,  # NEW
    reminder_offset: int | None = None,  # NEW (hours)
) -> Task:
    """Create a new task with optional priority, tags, due date, recurrence, reminder."""
    ...

@tool
def update_task(
    task_id: str,
    title: str | None = None,
    description: str | None = None,
    priority: str | None = None,  # NEW
    tags: list[str] | None = None,  # NEW
    due_date: str | None = None,  # NEW
    recurrence_rule: str | None = None,  # NEW
    reminder_offset: int | None = None,  # NEW
) -> Task:
    """Update task fields including new priority/tags/due_date/recurrence/reminder."""
    ...

@tool
def list_tasks(
    priority: str | None = None,  # NEW
    tags: list[str] | None = None,  # NEW
    search: str | None = None,  # NEW
    status: str = "pending",
    sort_by: str = "created_at",  # NEW
) -> list[Task]:
    """List tasks with optional filters and sorting."""
    ...
```

### Frontend Component Design

**Components to create/update**:

1. **TaskForm.tsx** (new version with all fields)
   - Title input (existing)
   - Description textarea (existing)
   - Priority dropdown/radio group (NEW)
   - Tags multi-select chips (NEW)
   - Due date picker with time (NEW)
   - Recurrence selector (dropdown + custom option) (NEW)
   - Reminder offset input (NEW)
   - Submit button

2. **TaskCard.tsx** (extend to display new fields)
   - Priority badge (color-coded: red=high, yellow=medium, green=low)
   - Tags as colored pills
   - Due date with overdue styling (red text if overdue)
   - Recurrence indicator (e.g., "🔄 daily")

3. **TaskListControls.tsx** (NEW)
   - Search input
   - Filter dropdown: priority, tags, status, due_date_range
   - Sort dropdown: priority, due_date, created_at
   - Apply/clear filters buttons

4. **TaskList.tsx** (update to use new filters/sorting)
   - Pass filters to API call
   - Display sorted results
   - Show "no tasks" message if empty

### Chatbot Integration

**Update system prompt** in `backend/app/agents/prompts.py`:

Add new intents and examples:
```
Intent: set_priority
Example: "Add a high priority task..." → priority="high"
Example: "Make this task urgent" → priority="high"

Intent: add_tags
Example: "Tag this work" → tags=["work"]
Example: "Mark as personal and urgent" → tags=["personal", "urgent"]

Intent: set_due_date
Example: "Due tomorrow" → due_date="<tomorrow's date>"
Example: "Due Friday at 3pm" → due_date="<Friday 3pm>"

Intent: set_recurrence
Example: "Repeat daily" → recurrence_rule="daily"
Example: "Weekly on Monday" → recurrence_rule="weekly:monday"

Intent: set_reminder
Example: "Remind me 1 day before" → reminder_offset=24 (hours)

Intent: filter_and_search
Example: "Show high priority work tasks" → list_tasks(priority="high", tags=["work"])
Example: "Search for budget" → list_tasks(search="budget")
```

### Project Structure

```
backend/
├── app/
│   ├── models/
│   │   └── task.py (extended with new fields)
│   ├── api/
│   │   └── tasks.py (extended with filters/sorting)
│   ├── mcp/
│   │   └── tools.py (extended MCP tool signatures)
│   └── agents/
│       └── prompts.py (extended system prompt)
├── alembic/
│   └── versions/
│       └── *_extend_task_intermediate_advanced.py (migration)

frontend/
├── app/
│   ├── components/
│   │   ├── TaskForm.tsx (extended)
│   │   ├── TaskCard.tsx (extended)
│   │   ├── TaskList.tsx (extended)
│   │   └── TaskListControls.tsx (NEW)
│   └── pages/
│       └── tasks/
│           └── page.tsx (uses new controls)
```

### Implementation Sequence

**Phase 1a: Data Layer**
1. Database Engineer: Extend Task model + create Alembic migration
2. Database Engineer: Apply migration to dev database

**Phase 1b: Backend API**
3. Backend Engineer: Update API routes (POST/PUT /tasks with new fields)
4. Backend Engineer: Add query param parsing for GET /tasks (filters/sorting)
5. Backend Engineer: Add database query functions (filter by priority, tag, search, sort)

**Phase 1c: MCP & Chatbot**
6. MCP Engineer: Extend MCP tool signatures (add new fields)
7. AI Agent Engineer: Update system prompt (new intents + examples)

**Phase 1d: Frontend**
8. Frontend Engineer: Create TaskForm.tsx with new fields
9. Frontend Engineer: Update TaskCard.tsx with new displays
10. Frontend Engineer: Create TaskListControls.tsx (filters/sorting)
11. Frontend Engineer: Update TaskList.tsx to use new controls

**Phase 1e: Integration & Testing**
12. Integration Tester: Test full flow (create task via UI, view with filters, use chatbot)

---

## Implementation Order & Dependencies

### Critical Path

1. **Alembic Migration** (blocks all other work) — Database Engineer
2. **Task Model Extension** — Database Engineer
3. **API Route Extensions** — Backend Engineer (depends on Task model)
4. **MCP Tool Updates** — MCP Engineer (depends on Task model)
5. **Chatbot Prompt Updates** — AI Agent Engineer (depends on MCP tools)
6. **Frontend Component Updates** — Frontend Engineer (depends on API routes)
7. **ChatKit Frontend Updates** — ChatKit Frontend Agent (depends on Chatbot prompt)
8. **End-to-End Testing** — Integration Tester (depends on all above)

### Parallelizable Work

- Frontend UI components can be developed in parallel with backend APIs (mocks for testing)
- MCP tool updates can proceed in parallel with API routes

---

## Validation & Acceptance

### Unit Tests

- Task model: priority/tags/due_date/recurrence/reminder fields validate correctly
- API routes: filters (priority, tag, status, due_date) work correctly; sorting works correctly
- MCP tools: signatures accept new fields; database saves correctly

### Integration Tests

- Create task via API with priority/tags → task saved and retrieved correctly
- Create recurring task → next instance created on completion
- Filter by priority → only matching tasks returned
- Filter by tag → only matching tasks returned
- Search by title → matching tasks returned
- Sort by priority/due_date → correct order

### End-to-End Tests

- Create task via UI with all new fields → appears in list with correct formatting
- Filter via UI → results update in real-time
- Sort via UI → list reorders correctly
- Chatbot: "Add high priority work task X due tomorrow" → task created with all fields
- Chatbot: "Show high priority work tasks" → filtered results returned

---

## Risks & Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| Breaking Phase 2-3 existing tasks | Low | High | Keep all new fields nullable; existing queries still work |
| Tag performance with large arrays | Low | Medium | Monitor; can migrate to normalized schema later if needed |
| Timezone bugs in due_date | Medium | Medium | Store UTC; convert to local on frontend; test DST transitions |
| Recurring task edge cases (leap years, etc.) | Medium | Low | Use simplified rules initially; handle edge cases iteratively |
| Chatbot NLP ambiguity (e.g., "work" as tag vs. action) | Medium | Medium | Train agent with examples; ask for clarification when ambiguous |

---

## Success Criteria (from Spec)

✅ All intermediate features testable and measurable (20 success criteria from spec)
✅ All advanced features testable and measurable (20 success criteria from spec)
✅ Chatbot integration complete (5 success criteria from spec)
✅ Multi-user isolation enforced
✅ Backward compatibility maintained
✅ All new code follows Phase 2-3 patterns (TypeScript, Pydantic, SQLModel)
✅ No new external dependencies

---

## Next Steps

1. **Database Engineer**: Create and apply Alembic migration
2. **Backend Engineer**: Extend API routes with new fields and filters
3. **MCP Engineer**: Update MCP tool signatures
4. **AI Agent Engineer**: Update chatbot system prompt
5. **Frontend Engineer**: Implement UI components
6. **ChatKit Frontend Agent**: Update chatbot UI
7. **Integration Tester**: End-to-end testing and validation

---

**Status**: Planning phase complete ✅
**Artifacts**: spec.md ✅, plan.md ✅
**Next Command**: `/sp.tasks` to break down into implementation tasks
