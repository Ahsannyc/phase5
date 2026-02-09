# Implementation Tasks: Phase 5 Part A – Intermediate & Advanced Features

**Feature**: 003-intermediate-advanced-features
**Branch**: `003-intermediate-advanced-features`
**Created**: 2026-02-08
**Plan Reference**: [plan.md](plan.md)
**Spec Reference**: [spec.md](spec.md)

---

## Overview

This task list breaks down Phase 5 Part A (Intermediate & Advanced features) into independently testable user stories with their implementation tasks. Each user story can be developed and tested independently, with clear dependencies shown below.

**Total Tasks**: 65 tasks across 7 user stories + setup/polish phases

**Parallel Execution Strategy**:
- Phase 1 (Setup): Execute sequentially (blocking prerequisites)
- Phase 2 (Foundational): Execute sequentially (blocking prerequisites for all features)
- Phase 3-9 (US1-US7): Execute independently; can run in parallel with minimal coordination
- Phase 10 (Polish): Execute after all features complete

**MVP Scope** (Minimum Viable Product - highest business value):
- US-1 (Task Prioritization): Core feature, quick to implement
- US-3 (Full-Text Search): Core feature, critical for task discovery
- US-6 (Recurring Task Automation): Advanced feature, high value

---

## Phase 1: Setup & Prerequisites

**Goal**: Initialize project structure and prepare for feature development

### Database & Environment Setup

- [ ] T001 Create Alembic migration file for Task model extensions at `backend/alembic/versions/*_extend_task_intermediate_advanced.py`
- [ ] T002 Add new columns to Task table: priority VARCHAR, tags JSONB, due_date TIMESTAMP, recurrence_rule VARCHAR, reminder_offset INTEGER
- [ ] T003 Create database indexes on due_date, priority, tags (GIN), recurrence_rule, and (user_id, status) composite
- [ ] T004 Apply Alembic migration to development database (test environment)
- [ ] T005 Verify database schema changes: run `alembic upgrade head && psql -c "\d task"` to confirm columns and indexes

### Project Structure & Configuration

- [ ] T006 Verify backend/app/models/ directory exists; create if missing
- [ ] T007 Verify backend/app/api/ directory exists; create if missing
- [ ] T008 Verify backend/mcp/ directory exists; create if missing
- [ ] T009 Verify frontend/app/components/ directory exists; create if missing
- [ ] T010 Create `.env.example` with KAFKA_BOOTSTRAP_SERVERS, COHERE_API_KEY, OPENAI_API_KEY placeholders (for future Part B)

---

## Phase 2: Foundational Features (Blocking Prerequisites)

**Goal**: Extend core Task model and API infrastructure to support all new features

### Task Model Extension

- [ ] T011 Extend Task model in `backend/app/models/task.py` with new fields:
  - `priority: str = Field(default="medium")` (low, medium, high)
  - `tags: list[str] = Field(default=[], sa_column=Column(JSON))`
  - `due_date: datetime | None = None`
  - `recurrence_rule: str | None = None`
  - `reminder_offset: int | None = None`
- [ ] T012 Add Pydantic validation: priority must be in ["low", "medium", "high"]
- [ ] T013 Add TaskPriority enum in `backend/app/models/task.py` for type safety
- [ ] T014 Create TaskSchema (Pydantic) for request/response serialization with all new fields
- [ ] T015 Verify Task model serializes/deserializes correctly with new fields (unit test)

### API Route Infrastructure

- [ ] T016 Extend `backend/app/api/tasks.py` POST /tasks endpoint to accept priority, tags, due_date, recurrence_rule, reminder_offset
- [ ] T017 [P] Extend `backend/app/api/tasks.py` PATCH /tasks/{task_id} endpoint to accept all new fields
- [ ] T018 Add query parameter parsing to GET /tasks for: priority, tag, search, status, due_date_range, sort_by
- [ ] T019 Create database query functions in `backend/app/crud/task.py`:
  - `filter_by_priority(user_id, priority)`
  - `filter_by_tag(user_id, tag)`
  - `search_tasks(user_id, search_term)`
  - `filter_by_status(user_id, status)`
  - `filter_by_due_date_range(user_id, due_date_range)`
  - `sort_tasks(tasks, sort_by)`
- [ ] T020 Test API routes with new fields (unit tests)

---

## Phase 3: User Story 1 – Task Prioritization (Priority: P1)

**Goal**: Enable users to mark tasks with priorities (low, medium, high) and filter/sort by priority

**Story Summary**: A user creates tasks with priorities (high, medium, low), sees them visually distinct in the task list, filters by priority, sorts by priority, and uses chatbot commands for priority-related operations.

**Independent Test**:
- User creates 3 tasks with different priorities
- Task list shows priority badges (color-coded: red=high, yellow=medium, green=low)
- User filters by "high priority" → only high-priority tasks shown
- User sorts by priority → tasks ordered high→medium→low
- User says "show high priority tasks" to chatbot → high-priority tasks returned

**Acceptance Criteria**:
- ✅ Priority field saved correctly in database
- ✅ Priority displayed in UI with color coding
- ✅ Filter by priority returns correct tasks
- ✅ Sort by priority reorders list correctly
- ✅ Chatbot understands priority commands

### Task Prioritization Implementation

- [ ] T021 [US1] Create PriorityBadge component in `frontend/app/components/PriorityBadge.tsx` with color-coding (high=red, medium=yellow, low=green)
- [ ] T022 [P] [US1] Add priority dropdown to TaskForm.tsx with options: low, medium, high
- [ ] T023 [P] [US1] Update TaskCard.tsx to display priority badge via PriorityBadge component
- [ ] T024 [US1] Add priority filter control to TaskListControls.tsx (dropdown or radio group)
- [ ] T025 [P] [US1] Implement priority filter in GET /tasks API (filter_by_priority CRUD function)
- [ ] T026 [US1] Test priority filtering: verify only matching priorities returned
- [ ] T027 [P] [US1] Implement priority sorting in GET /tasks API (sort_tasks CRUD function)
- [ ] T028 [US1] Test priority sorting: verify correct order (high→medium→low)
- [ ] T029 [US1] Add priority intent to chatbot system prompt in `backend/app/agents/prompts.py`:
  - Example: "Add high priority task buy groceries" → priority="high"
  - Example: "Make this urgent" → priority="high"
- [ ] T030 [US1] Test chatbot priority commands end-to-end (create via chat, verify in UI)

**US1 Complete**: Task prioritization fully functional in UI and chatbot

---

## Phase 4: User Story 2 – Task Tagging & Organization (Priority: P1)

**Goal**: Enable users to create and apply custom tags to tasks, filter and search by tags

**Story Summary**: A user creates tasks with custom tags (e.g., "work", "personal"), applies multiple tags per task, filters by tag, and uses chatbot commands for tag operations.

**Independent Test**:
- User creates tasks and applies tags (work, personal, urgent)
- Task list shows tags as colored pills
- User filters by tag "work" → only work-tagged tasks shown
- User applies multiple tags to same task; both filters show the task
- User says "tag this urgent" to chatbot → tag applied

**Acceptance Criteria**:
- ✅ Tags saved correctly in database (JSON array)
- ✅ Tags displayed in UI as colored pills
- ✅ Filter by tag returns correct tasks
- ✅ Multiple tags per task supported
- ✅ Chatbot understands tag commands

### Task Tagging Implementation

- [ ] T031 [US2] Create TagPill component in `frontend/app/components/TagPill.tsx` to display single tag as colored pill
- [ ] T032 [P] [US2] Add tags multi-select input to TaskForm.tsx (text input with autocomplete or chip input)
- [ ] T033 [US2] Update TaskCard.tsx to display tags via TagPill component (iterate over tags array)
- [ ] T034 [P] [US2] Add tag filter control to TaskListControls.tsx (multi-select with autocomplete)
- [ ] T035 [US2] Create tag list/autocomplete data source in `backend/app/crud/task.py`:
  - `get_user_tags(user_id)` → returns all unique tags for user
- [ ] T036 [US2] Implement tag filtering in GET /tasks API (filter_by_tag CRUD function; OR logic if multiple tags)
- [ ] T037 [US2] Test tag filtering: verify single tag and multiple tags work correctly
- [ ] T038 [P] [US2] Add tag intent to chatbot system prompt:
  - Example: "Tag this work" → tags=["work"]
  - Example: "Mark as personal and urgent" → tags=["personal", "urgent"]
- [ ] T039 [US2] Implement tag autocomplete endpoint in API: GET /api/{user_id}/tags
- [ ] T040 [US2] Test chatbot tag commands end-to-end (tag via chat, verify in UI)

**US2 Complete**: Task tagging fully functional in UI and chatbot

---

## Phase 5: User Story 3 – Full-Text Search (Priority: P1)

**Goal**: Enable users to quickly find tasks by searching title and description

**Story Summary**: A user searches for keywords (e.g., "budget", "meeting"), results appear with matching tasks, and chatbot understands search commands.

**Independent Test**:
- User enters "project" in search bar
- Task list filters to show only tasks with "project" in title or description
- User searches for partial word "meet" → matches "meeting", "meetup"
- User says "search for budget" to chatbot → matching tasks returned

**Acceptance Criteria**:
- ✅ Search is case-insensitive
- ✅ Partial word matches work
- ✅ Search results appear in <1 second
- ✅ Chatbot search commands work

### Full-Text Search Implementation

- [ ] T041 [US3] Add search input field to TaskListControls.tsx with debounced onChange handler
- [ ] T042 [P] [US3] Implement search filtering in GET /tasks API (ILIKE query on title and description)
- [ ] T043 [US3] Create search CRUD function in `backend/app/crud/task.py`:
  - `search_tasks(user_id, search_term)` → returns tasks where title ILIKE or description ILIKE search_term
- [ ] T044 [US3] Test search: verify case-insensitive, partial word matches, performance <1s
- [ ] T045 [P] [US3] Add search intent to chatbot system prompt:
  - Example: "Search for groceries" → search="groceries"
  - Example: "Find tasks with meeting" → search="meeting"
- [ ] T046 [US3] Test chatbot search commands end-to-end (search via chat, verify results)

**US3 Complete**: Full-text search fully functional in UI and chatbot

---

## Phase 6: User Story 4 – Advanced Filtering (Priority: P1)

**Goal**: Enable users to combine multiple filters (status, priority, tag, due date) to narrow task list

**Story Summary**: A user applies filters: incomplete status + high priority + work tag + overdue due date. Task list shows only tasks matching ALL criteria. Filter combinations can be saved/cleared.

**Independent Test**:
- User applies filters: status=incomplete AND priority=high AND tag=work
- Task list shows only incomplete, high-priority work tasks
- User removes one filter (e.g., priority); list updates to show tasks matching remaining filters
- User says "show pending high priority work tasks" to chatbot → filtered results returned

**Acceptance Criteria**:
- ✅ Multiple filters combine with AND logic
- ✅ Filters work correctly in all combinations
- ✅ Removing filters updates results immediately
- ✅ Empty result set shows "no tasks" message
- ✅ Chatbot understands complex filter commands

### Advanced Filtering Implementation

- [ ] T047 [P] [US4] Add status filter (pending, completed) to TaskListControls.tsx
- [ ] T048 [P] [US4] Add due_date_range filter (today, week, month, overdue) to TaskListControls.tsx
- [ ] T049 [US4] Implement multi-filter combination in GET /tasks API (AND logic: all filters applied)
- [ ] T050 [US4] Create due_date_range filter CRUD function:
  - `filter_by_due_date_range(user_id, range)` → today/week/month/overdue
- [ ] T051 [US4] Test filter combinations: verify AND logic, empty results handling
- [ ] T052 [P] [US4] Add complex filter intent to chatbot system prompt:
  - Example: "Show pending high priority work tasks" → status="pending", priority="high", tags=["work"]
- [ ] T053 [US4] Test chatbot complex filter commands end-to-end

**US4 Complete**: Advanced filtering fully functional

---

## Phase 7: User Story 5 – Flexible Sorting (Priority: P1)

**Goal**: Enable users to sort tasks by multiple criteria (created date, due date, priority, title, status)

**Story Summary**: A user selects sort criteria (e.g., due date ascending, priority descending). Task list reorders immediately. Sorting works on filtered results.

**Independent Test**:
- User selects "sort by due date" → tasks ordered earliest→latest
- User changes sort to "priority (high→low)" → tasks ordered high→medium→low
- User applies filters then sorts; sorting works on filtered results
- User says "sort by priority" to chatbot → results reordered

**Acceptance Criteria**:
- ✅ All sort criteria work (date, priority, title, status, created date)
- ✅ Ascending/descending toggle works
- ✅ Sorting applies to filtered results
- ✅ Default sort is creation date

### Flexible Sorting Implementation

- [ ] T054 [US5] Add sort dropdown to TaskListControls.tsx with options: created_at, due_date, priority, title, status
- [ ] T055 [P] [US5] Add sort direction toggle (ascending/descending) to TaskListControls.tsx
- [ ] T056 [US5] Implement sorting in GET /tasks API using sort_tasks CRUD function
- [ ] T057 [US5] Create sort_tasks function that handles all criteria and directions
- [ ] T058 [P] [US5] Test all sort combinations: verify correct order, performance
- [ ] T059 [US5] Add sort intent to chatbot system prompt:
  - Example: "Sort by priority" → sort_by="priority"
  - Example: "Show newest first" → sort_by="-created_at"
- [ ] T060 [US5] Test chatbot sort commands end-to-end

**US5 Complete**: Flexible sorting fully functional

---

## Phase 8: User Story 6 – Recurring Task Automation (Priority: P2)

**Goal**: Enable users to create recurring tasks that auto-generate next instances

**Story Summary**: A user creates a recurring task (e.g., daily standup). When today's instance is marked complete, tomorrow's instance auto-creates. Recurrence rules are simple (daily, weekly:monday, monthly:15).

**Independent Test**:
- User creates daily recurring task
- User marks today's instance complete
- Tomorrow's instance appears automatically in task list
- Recurrence persists over multiple cycles (week of daily tasks)
- User deletes recurring task; future instances don't appear

**Acceptance Criteria**:
- ✅ Recurrence rules parsed correctly
- ✅ Next instance created on completion
- ✅ Due dates calculated correctly for each instance
- ✅ Deletion stops future instances
- ✅ Chatbot understands recurrence commands

### Recurring Task Implementation

- [ ] T061 [P] [US6] Add recurrence selector to TaskForm.tsx (dropdown: daily, weekly, monthly, yearly, custom)
- [ ] T062 [P] [US6] Create recurrence parser in `backend/app/utils/recurrence.py`:
  - `parse_recurrence_rule(rule: str, start_date: datetime) → datetime` (calculate next date)
  - Supports: "daily", "weekly:monday", "weekly:tue-thu", "monthly:15", "yearly:march-15"
- [ ] T063 [US6] Add recurring task auto-creation logic to complete_task endpoint:
  - When task marked complete AND recurrence_rule exists → create next instance with due_date calculated from recurrence_rule
- [ ] T064 [P] [US6] Test recurrence calculation: verify next dates correct for all rule types
- [ ] T065 [US6] Test recurring task deletion: verify future instances don't appear (filter by recurrence_rule)
- [ ] T066 [US6] Update TaskCard.tsx to show recurrence indicator (e.g., "🔄 daily")
- [ ] T067 [P] [US6] Add recurrence intent to chatbot system prompt:
  - Example: "Create daily standup task" → recurrence_rule="daily"
  - Example: "Make this weekly on Monday" → recurrence_rule="weekly:monday"
- [ ] T068 [US6] Test chatbot recurrence commands end-to-end

**US6 Complete**: Recurring tasks fully functional

---

## Phase 9: User Story 7 – Due Dates & Smart Reminders (Priority: P2)

**Goal**: Enable users to set due dates and reminders for tasks

**Story Summary**: A user creates a task with due date (e.g., "tomorrow") and sets a reminder (e.g., "1 day before"). Due date displays with overdue highlighting. Reminders are logged and ready for future delivery (Part B).

**Independent Test**:
- User creates task with due date = tomorrow
- Due date displays in task card
- User sets reminder = 1 day before
- Reminder is stored and can be retrieved
- User creates task with due date = yesterday, status = incomplete
- Task is highlighted as overdue (red)
- User marks task complete; overdue highlighting removed

**Acceptance Criteria**:
- ✅ Due dates stored in UTC
- ✅ Due dates displayed in user's local timezone
- ✅ Overdue tasks highlighted in red
- ✅ Reminders stored correctly
- ✅ Chatbot understands due date and reminder commands

### Due Dates & Reminders Implementation

- [ ] T069 [P] [US7] Add due date picker to TaskForm.tsx (date + time inputs or datetime picker component)
- [ ] T070 [P] [US7] Add reminder offset input to TaskForm.tsx (hours or days before due date)
- [ ] T071 [US7] Update TaskCard.tsx to display due_date with formatting and overdue highlighting:
  - Format: "Due Tomorrow" or "Due Mar 15" (localized)
  - Red text/background if overdue AND status != completed
- [ ] T072 [US7] Create timezone conversion utility in `frontend/lib/timezone.ts`:
  - `convertToLocal(utcDate: datetime, userTimezone: string) → datetime`
  - `convertToUTC(localDate: datetime, userTimezone: string) → datetime`
- [ ] T073 [P] [US7] Implement due_date and reminder_offset validation in API (non-null if either provided)
- [ ] T074 [US7] Create reminder notification logic in `backend/app/utils/reminders.py`:
  - `calculate_reminder_time(due_date: datetime, reminder_offset: int) → datetime`
- [ ] T075 [US7] Test due date display: verify UTC storage, local display, timezone handling
- [ ] T076 [P] [US7] Test overdue highlighting: verify tasks with past due_date are highlighted
- [ ] T077 [US7] Add due date intent to chatbot system prompt:
  - Example: "Due tomorrow" → due_date="<tomorrow>"
  - Example: "Due Friday at 3pm" → due_date="<Friday 3pm>"
- [ ] T078 [US7] Add reminder intent to chatbot system prompt:
  - Example: "Remind me 1 day before" → reminder_offset=24 (hours)
  - Example: "Remind me 1 hour before" → reminder_offset=1
- [ ] T079 [US7] Test chatbot due date and reminder commands end-to-end

**US7 Complete**: Due dates and reminders fully functional

---

## Phase 10: Polish & Cross-Cutting Concerns

**Goal**: Final documentation, testing, and preparation for production

### Comprehensive Testing

- [ ] T080 [P] Run all unit tests: models, CRUD functions, API routes
- [ ] T081 [P] Run all component tests: TaskForm, TaskCard, TaskListControls
- [ ] T082 Run end-to-end tests: UI workflow (create → filter → sort → complete)
- [ ] T083 Run end-to-end tests: Chatbot workflow (chat commands → verify UI updates)
- [ ] T084 Test multi-user isolation: verify user A cannot see user B's tasks/filters
- [ ] T085 Test timezone handling: create task in EST, view in PST, verify correct time
- [ ] T086 Test edge cases: empty results, special characters in search, tag deletion

### Documentation & Cleanup

- [ ] T087 [P] Update README.md with Phase 5 Part A section:
  - New features (priorities, tags, search, filter, sort, recurring, due dates)
  - Setup instructions (Alembic migration, database schema)
  - API documentation (new query params, response schemas)
- [ ] T088 [P] Create API_CHANGES.md documenting all endpoint changes
- [ ] T089 Create CHATBOT_COMMANDS.md with examples of all new chatbot intents
- [ ] T090 [P] Update ARCHITECTURE.md with new data model and query patterns
- [ ] T091 Clean up any temporary code or debug logs
- [ ] T092 Run linter/formatter: `black`, `isort`, `eslint`, `prettier`

### Acceptance & Handoff

- [ ] T093 [P] Create smoke test script to verify all features work end-to-end
- [ ] T094 [P] Verify database schema matches plan (indexes, types, constraints)
- [ ] T095 Create DEPLOYMENT_NOTES.md for moving to production
- [ ] T096 [P] Run load test: verify performance targets (search <1s, filter <500ms)
- [ ] T097 Prepare for Part B handoff: document any assumptions or limitations for Kafka/Dapr integration

**Phase 10 Complete**: All features polished and documented

---

## Task Dependencies & Execution Graph

### Critical Path (Sequential Must-Haves)

```
Phase 1 (Setup) → Phase 2 (Foundational) → Phases 3-9 (User Stories) → Phase 10 (Polish)
```

**Phase 1 Blocks Everything**: Alembic migration and Task model must be in place before any feature work.

**Phase 2 Blocks User Stories**: API routes and CRUD functions must exist before UI/chatbot updates.

**User Stories Parallelizable**:
- US1, US2, US3, US4, US5 (Intermediate features) can run in parallel after Phase 2 complete
- US6, US7 (Advanced features) can run in parallel after Phase 2 complete
- Recommendation: US1 + US3 in parallel (prioritization + search = highest value), then US2/US4/US5, then US6/US7

### Parallel Execution Example

**Week 1**:
- Database Engineer: Phase 1 (T001-T010) + Phase 2 database (T011-T015)
- Backend Engineer: Phase 2 API (T016-T020) in parallel with DB work

**Week 2**:
- **Parallel Track A** (Frontend): US1 UI (T021-T024), US3 Search (T041-T042)
- **Parallel Track B** (Backend): US1 API (T025-T026), US3 API (T042-T044)
- **Parallel Track C** (Chatbot): US1-US3 prompts (T029, T038, T045)

**Week 3**:
- Remaining US features (US2, US4, US5, US6, US7) in same parallel pattern
- Integration testing begins (T082-T085)

**Week 4**:
- Polish & documentation (T087-T097)
- Final testing & handoff

---

## MVP Scope Recommendation

**Minimum Viable Product** (highest value with minimum scope):

1. **T001-T020** (Phase 1-2): Database + Core API (2-3 days)
2. **T021-T030** (Phase 3 - US1): Task prioritization (1-2 days)
3. **T041-T046** (Phase 5 - US3): Search (1-2 days)
4. **T061-T068** (Phase 8 - US6): Recurring tasks (2-3 days)

**MVP Deliverables**: Priorities + Search + Recurring Tasks = 80% of value with 40% of effort

**Post-MVP** (if time/resources): Add Tags (US2), Filtering (US4), Sorting (US5), Due Dates (US7)

---

## Acceptance Test Plan

| Test ID | Scenario | Expected Result | Status |
|---------|----------|-----------------|--------|
| AT-1.1 | Create high-priority task | Priority saved, displays with red badge | ⏳ |
| AT-1.2 | Filter by priority | Only matching priority tasks shown | ⏳ |
| AT-2.1 | Apply multiple tags | All tags visible as pills | ⏳ |
| AT-2.2 | Filter by tag "work" | Only work-tagged tasks shown | ⏳ |
| AT-3.1 | Search for "budget" | Tasks with "budget" in title/description returned | ⏳ |
| AT-4.1 | Apply status+priority+tag filters | AND logic: all criteria match | ⏳ |
| AT-5.1 | Sort by due date | Tasks ordered earliest→latest | ⏳ |
| AT-6.1 | Create daily recurring task | Next instance auto-creates on completion | ⏳ |
| AT-7.1 | Create task with due date tomorrow | Displays "Due Tomorrow" in card | ⏳ |
| AT-7.2 | Set task due date to yesterday | Displays overdue (red) | ⏳ |
| AT-CHAT-1 | Chatbot: "add high priority task" | Task created with priority=high | ⏳ |
| AT-CHAT-2 | Chatbot: "show work tasks" | Work-tagged tasks returned | ⏳ |
| AT-CHAT-3 | Chatbot: "search for budget" | Matching tasks returned | ⏳ |

---

**Status**: Tasks ready for implementation
**MVP Path**: T001-T020, T021-T030, T041-T046, T061-T068 = 40 tasks, ~10 days
**Full Scope**: All 97 tasks = ~25 days
**Next Step**: Begin Phase 1 setup tasks
