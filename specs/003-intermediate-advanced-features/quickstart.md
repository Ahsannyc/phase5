# Quickstart: Phase 5 Part A – Intermediate & Advanced Features

**Feature**: Phase 5 Part A – Intermediate & Advanced Todo Features
**Branch**: `003-intermediate-advanced-features`
**Date**: 2026-02-09

This document provides a quick reference for getting started with Phase 5 Part A implementation.

---

## Implementation Checklist

### Phase 1: Database (Database Engineer)
- [ ] Review `data-model.md` and `plan.md` for schema changes
- [ ] Create Alembic migration: `extend_task_intermediate_advanced_features.py`
  - [ ] Add 5 new columns (priority, tags, due_date, recurrence_rule, reminder_offset)
  - [ ] Create indexes (priority, due_date, tags GIN, recurrence_rule, user_status composite)
  - [ ] Test migration: `alembic upgrade head`
  - [ ] Test rollback: `alembic downgrade -1` (verify reversibility)
- [ ] Verify Neon PostgreSQL schema: `\d task` (show table structure)
- [ ] Update `backend/app/models/task.py` with new fields and enums

### Phase 2: Backend API (Backend Engineer)
- [ ] Extend `backend/app/api/tasks.py`
  - [ ] Update POST /tasks (accept priority, tags, due_date, recurrence_rule, reminder_offset)
  - [ ] Update PUT /tasks/{task_id} (same fields)
  - [ ] Extend GET /tasks (add query params: priority, tag, search, status, sort)
  - [ ] Add helper functions (filter by priority, filter by tag, search by title, sort by field)
- [ ] Add validation (Pydantic models for request/response)
- [ ] Add error handling (400 for invalid priority, 422 for validation errors)
- [ ] Test all endpoints: `pytest backend/tests/test_api_tasks.py`

### Phase 3: MCP Tools (MCP Engineer)
- [ ] Extend `backend/mcp/tools.py`
  - [ ] Update `add_task()` signature (add priority, tags, due_date, recurrence_rule, reminder_offset)
  - [ ] Update `update_task()` signature (same new fields)
  - [ ] Update `list_tasks()` signature (add filter params: priority, tags, search, sort_by)
- [ ] Verify MCP tool descriptions match new fields
- [ ] Test MCP tools: `pytest backend/tests/test_mcp_tools.py`

### Phase 4: Chatbot Prompt (AI Agent Engineer)
- [ ] Update `backend/app/agents/prompts.py`
  - [ ] Add new intents: set_priority, add_tags, set_due_date, set_recurrence, set_reminder, filter_and_search
  - [ ] Add examples for each intent (examples from spec.md user stories)
  - [ ] Test with agent: "Add high priority task buy milk tomorrow"
  - [ ] Test with agent: "Show high priority work tasks"

### Phase 5: Frontend UI (Frontend Engineer)
- [ ] Create/update `frontend/app/components/TaskForm.tsx`
  - [ ] Add priority dropdown (Low/Medium/High)
  - [ ] Add tags multi-select or chips input
  - [ ] Add due date picker (date + time)
  - [ ] Add recurrence selector (daily/weekly/monthly/yearly + custom)
  - [ ] Add reminder offset input (hours/days)
- [ ] Update `frontend/app/components/TaskCard.tsx`
  - [ ] Display priority badge (color-coded: red/yellow/green)
  - [ ] Display tags as colored pills
  - [ ] Display due date (with red text if overdue)
  - [ ] Display recurrence indicator (if set)
- [ ] Create `frontend/app/components/TaskListControls.tsx`
  - [ ] Search input
  - [ ] Filter dropdown (priority, tag, status, due date range)
  - [ ] Sort dropdown (created_at, due_date, priority, title, status)
- [ ] Update `frontend/app/components/TaskList.tsx`
  - [ ] Pass filters to API call
  - [ ] Display sorted/filtered results
  - [ ] Show "no tasks" message when empty
- [ ] Test components: `npm test frontend/`

### Phase 6: ChatKit Frontend (ChatKit Frontend Agent)
- [ ] Ensure ChatKit displays task details (priorities, tags, due dates)
- [ ] Test chatbot commands:
  - [ ] "Add high priority task..."
  - [ ] "Show high priority work tasks"
  - [ ] "Make task daily"
  - [ ] "Remind me about X"

### Phase 7: Integration Testing (Integration Tester)
- [ ] Test end-to-end flows:
  - [ ] Create task via UI with all fields
  - [ ] View task with all details displayed
  - [ ] Filter by priority
  - [ ] Filter by tag
  - [ ] Search for task
  - [ ] Sort by due date
  - [ ] Mark recurring task complete → next instance appears
  - [ ] Create task via chatbot: "Add high priority work task due tomorrow"
  - [ ] List tasks via chatbot with filters
- [ ] Test error cases:
  - [ ] Invalid priority
  - [ ] Too many tags
  - [ ] Invalid due date (past)
  - [ ] Invalid recurrence rule
- [ ] Test user isolation:
  - [ ] User A cannot see User B's tasks
  - [ ] Filters respect user_id

---

## Code Examples

### Creating a Task with All Fields (API)

```bash
curl -X POST http://localhost:8000/api/users/123/tasks \
  -H "Authorization: Bearer <JWT>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Weekly project review",
    "description": "Review completed tasks and plan next week",
    "priority": "high",
    "tags": ["work", "management"],
    "due_date": "2026-02-15T15:00:00Z",
    "recurrence_rule": "weekly:friday",
    "reminder_offset": 24
  }'
```

### Filtering Tasks (API)

```bash
# Get high priority work tasks that are pending
curl http://localhost:8000/api/users/123/tasks \
  "?priority=high&tag=work&status=pending&sort=-due_date" \
  -H "Authorization: Bearer <JWT>"
```

### Chatbot Command Examples

```
User: "Add high priority task buy milk due tomorrow"
Agent: Creates task with priority="high", due_date=tomorrow

User: "Show pending high priority tasks"
Agent: Returns filtered list_tasks(status="pending", priority="high")

User: "Make this task repeat weekly on Monday"
Agent: Updates task with recurrence_rule="weekly:monday"

User: "Remind me 1 day before this task"
Agent: Updates task with reminder_offset=24 (hours)
```

---

## Testing Examples

### Unit Test: Priority Enum

```python
def test_task_priority_enum():
    from app.models.task import TaskPriority
    assert TaskPriority.LOW == "low"
    assert TaskPriority.MEDIUM == "medium"
    assert TaskPriority.HIGH == "high"
```

### Integration Test: Filter by Priority

```python
def test_filter_tasks_by_priority(client, user_token):
    # Create high and low priority tasks
    client.post("/api/users/123/tasks",
      json={"title": "Task 1", "priority": "high"},
      headers={"Authorization": f"Bearer {user_token}"})
    client.post("/api/users/123/tasks",
      json={"title": "Task 2", "priority": "low"},
      headers={"Authorization": f"Bearer {user_token}"})

    # Filter by high priority
    response = client.get("/api/users/123/tasks?priority=high",
      headers={"Authorization": f"Bearer {user_token}"})

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "Task 1"
```

### End-to-End Test: Recurring Task

```python
def test_recurring_task_creates_next_instance():
    # Create recurring task
    task = create_task(
      title="Daily standup",
      recurrence_rule="daily",
      due_date=today)

    # Mark complete
    complete_task(task.id)

    # Verify next instance created
    next_task = get_task_by_title("Daily standup")
    assert next_task.due_date == tomorrow
    assert next_task.status == "pending"
```

---

## Configuration & Environment

### Backend Environment Variables

```bash
# .env (development)
DATABASE_URL=postgresql://user:password@localhost:5432/todo_db
BETTER_AUTH_SECRET=your-jwt-secret
```

### Frontend Environment Variables

```bash
# .env.local (development)
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

---

## Key Files to Review

| File | Purpose | Status |
|------|---------|--------|
| `spec.md` | Feature specification with user stories | ✅ COMPLETE |
| `plan.md` | Implementation plan with design decisions | ✅ COMPLETE |
| `research.md` | Phase 0 research findings | ✅ COMPLETE |
| `data-model.md` | Database schema and entities | ✅ COMPLETE |
| `tasks.md` | Implementation tasks (Phase 2 output) | ⏭️ TODO |
| `backend/app/models/task.py` | SQLModel Task class | ⏭️ TO BE EXTENDED |
| `backend/app/api/tasks.py` | FastAPI endpoints | ⏭️ TO BE EXTENDED |
| `backend/mcp/tools.py` | MCP tool definitions | ⏭️ TO BE EXTENDED |
| `frontend/app/components/TaskForm.tsx` | Task form component | ⏭️ TO BE UPDATED |
| `frontend/app/components/TaskList.tsx` | Task list component | ⏭️ TO BE UPDATED |

---

## Success Criteria (Phase 5 Part A)

- ✅ Spec: User stories with acceptance scenarios (7 stories)
- ✅ Plan: Technical design and implementation roadmap
- ✅ Research: All technical decisions documented and justified
- ✅ Data Model: Schema designed; backward-compatible migration ready
- ⏭️ Tasks: Implementation tasks broken down and assigned
- ⏭️ Code: All features implemented and tested
- ⏭️ Integration: Full end-to-end testing passing
- ⏭️ Documentation: README and deployment notes updated

---

## Troubleshooting

### Alembic Migration Fails
- Verify PostgreSQL is running: `psql --version`
- Check DATABASE_URL: `echo $DATABASE_URL`
- Verify Neon PostgreSQL connection: `psql $DATABASE_URL -c "SELECT version();"`
- Check migration file syntax: `head alembic/versions/*_extend_task*.py`

### API Tests Fail
- Verify FastAPI is running: `curl http://localhost:8000/health`
- Check JWT token validity
- Verify user_id in path matches JWT sub claim
- Check database has test fixtures

### Frontend Component Errors
- Verify TypeScript compilation: `npm run build frontend/`
- Check imports: `grep -r "TaskForm" frontend/`
- Verify Tailwind classes: `npm run lint frontend/`

---

## Next Steps

1. ✅ **Specification** (spec.md) — Complete
2. ✅ **Planning** (plan.md, research.md, data-model.md) — Complete
3. ⏭️ **Tasks Generation** (tasks.md) — Run `/sp.tasks`
4. ⏭️ **Implementation** — Agents execute according to workflow
5. ⏭️ **Testing & Validation** — Integration tester verifies end-to-end
6. ⏭️ **Documentation** — Update README and deployment notes

**Start Implementation**: All planning artifacts are ready. Proceed with `/sp.tasks` to generate implementation tasks.

