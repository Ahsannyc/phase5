# Feature Specification: Phase 5 Part A – Intermediate & Advanced Todo Features

**Feature Branch**: `003-intermediate-advanced-features`
**Created**: 2026-02-08
**Status**: Ready for Planning
**Scope**: Feature implementation only (no cloud deployment, no Dapr, no Kafka)
**Constitution Reference**: [Phase 5 Constitution](../../.specify/memory/constitution.md)

---

## Overview & Purpose

Extend the existing Todo application (Phase 2 full-stack + Phase 3 AI chatbot) by implementing all **Intermediate Level features** and all **Advanced Level features** as defined in the hackathon Phase 5 scope.

This specification covers **only Part A** (feature implementation):
- **Intermediate Features**: Priorities, Tags, Search, Filter, Sort
- **Advanced Features**: Recurring Tasks, Due Dates & Reminders

**Out of Scope**: Cloud deployment (AKS/GKE/OKE), Dapr, Kafka, CI/CD, event-driven architecture — these are Part B & C.

The features must work seamlessly in both:
- **Web UI** (Phase 2 frontend with Next.js)
- **AI Chatbot** (Phase 3 natural language interface)

---

## User Scenarios & Testing

### User Story US-1: Task Prioritization (Priority: P1)

A power user wants to mark tasks as High, Medium, or Low priority to focus on what matters most. Priorities are visually distinct in the task list, sortable, and filterable. The chatbot understands priority-related commands.

**Why this priority**: Prioritization is essential for time management and focus. Users often have more tasks than time and need to identify critical items quickly.

**Independent Test**: A user creates tasks with different priorities. The task list shows priorities visually distinct (color-coded badges). User filters by "high priority" and sees only high-priority tasks. Sorting by priority reorders the list correctly.

**Acceptance Scenarios**:

1. **Given** a user creates a task and sets priority to "high", **When** the task is saved, **Then** the task displays a high-priority indicator (color, icon, or badge)
2. **Given** a user has tasks with mixed priorities, **When** they filter by priority "high", **Then** only high-priority tasks appear
3. **Given** a user sorts tasks by priority, **When** they view the list, **Then** tasks are ordered high → medium → low
4. **Given** a user says "show my high priority tasks", **When** the chatbot processes the command, **Then** high-priority tasks are listed

---

### User Story US-2: Task Tagging & Organization (Priority: P1)

A user wants to organize tasks with custom tags (e.g., "work", "personal", "urgent", "learning") to group related tasks. Tags are user-defined, can be applied to multiple tasks, and support filtering and searching.

**Why this priority**: Tags provide flexible organization beyond a simple hierarchy. Users have diverse task types and need to organize them by context, not just status.

**Independent Test**: A user creates tasks and applies tags (work, personal). They filter by tag "work" to see only work-related tasks. They can create new tags on-the-fly. Multiple filters combine correctly.

**Acceptance Scenarios**:

1. **Given** a user creates a task and applies tags, **When** the task is saved, **Then** tags are visible as colored pills in the task card
2. **Given** a user has tasks with tags, **When** they click a tag, **Then** all tasks with that tag are displayed
3. **Given** a user applies multiple tags to different tasks, **When** they filter by one tag, **Then** only tasks with that tag appear (filtering is inclusive — OR logic for multiple tags)
4. **Given** a user says "tag this task as urgent", **When** the chatbot processes the command, **Then** the tag is applied and visible

---

### User Story US-3: Full-Text Search (Priority: P1)

A user wants to quickly find tasks by searching for keywords in task titles and descriptions. Search results appear instantly and are sortable.

**Why this priority**: Search is critical for task discovery when task count grows. Users should be able to find tasks without scrolling through a long list.

**Independent Test**: A user searches for "project X". Tasks containing "project X" in title or description appear in results. Searching for partial words ("meet") returns tasks with "meeting", "meetup", etc.

**Acceptance Scenarios**:

1. **Given** a user enters a search term in the search bar, **When** they press enter, **Then** tasks matching the search term (title or description) appear
2. **Given** a user searches for a partial word, **When** they view results, **Then** tasks with that substring are returned (case-insensitive)
3. **Given** a user has multiple search results, **When** they apply sorting, **Then** results are sorted correctly
4. **Given** a user says "search for budget", **When** the chatbot processes the command, **Then** tasks with "budget" are returned

---

### User Story US-4: Advanced Filtering (Priority: P1)

A user wants to filter tasks by multiple criteria (status, priority, tag, due date) to narrow down the task list. Filters combine logically (AND — all criteria must match).

**Why this priority**: Advanced filtering is essential for power users managing large task lists. Combining filters helps users focus on specific subsets of work.

**Independent Test**: A user applies filters: status=incomplete, priority=high, tag=work. Task list shows only incomplete, high-priority work tasks. Changing one filter updates results in real-time.

**Acceptance Scenarios**:

1. **Given** a user applies multiple filters (e.g., status=incomplete AND priority=high AND tag=work), **When** they view the task list, **Then** only tasks matching ALL criteria appear
2. **Given** filters are applied, **When** the user removes one filter, **Then** the list updates to show tasks matching remaining filters
3. **Given** no tasks match the applied filters, **When** the user views the result, **Then** a "no tasks" message appears
4. **Given** a user says "show pending high priority work tasks", **When** the chatbot processes the command, **Then** filtered results appear

---

### User Story US-5: Flexible Sorting (Priority: P1)

A user wants to sort tasks by multiple criteria (created date, due date, priority, title, status) to organize the list according to their workflow.

**Why this priority**: Sorting is essential for task management. Users should be able to view tasks in the order most relevant to their current workflow (e.g., due date for deadline-driven work, priority for focus-driven work).

**Independent Test**: A user sorts tasks by due date (ascending). Most urgent tasks appear first. They change sort to priority (descending). High-priority tasks appear first.

**Acceptance Scenarios**:

1. **Given** a user selects "sort by due date", **When** they view the task list, **Then** tasks are ordered from earliest to latest due date
2. **Given** a user selects "sort by priority (high to low)", **When** they view the task list, **Then** high-priority tasks appear first
3. **Given** a user sorts by title, **When** they view the task list, **Then** tasks are alphabetically ordered
4. **Given** a user says "sort by priority", **When** the chatbot processes the command, **Then** tasks are reordered

---

### User Story US-6: Recurring Task Automation (Priority: P2)

A user wants to create recurring tasks (daily standup, weekly review, monthly planning) that automatically create new instances. When today's instance is marked complete, tomorrow's instance appears.

**Why this priority**: Recurring tasks eliminate manual data entry and are essential for routine work. This is a core productivity feature.

**Independent Test**: A user creates a recurring task (daily standup). The task is marked complete today. Tomorrow, a new instance appears automatically. The task repeats correctly for a week.

**Acceptance Scenarios**:

1. **Given** a user creates a recurring task (daily), **When** they mark today's instance complete, **Then** tomorrow's instance is automatically created
2. **Given** a user creates a weekly recurring task (Monday), **When** they mark this Monday's instance complete, **Then** next Monday's instance is created
3. **Given** a recurring task is deleted, **When** the user views their task list, **Then** future instances are not created
4. **Given** a user says "create a daily standup task", **When** the chatbot processes the command, **Then** a recurring task is created with daily recurrence

---

### User Story US-7: Due Dates & Smart Reminders (Priority: P2)

A user wants to assign due dates to tasks and set reminders (e.g., "remind me 1 day before"). Overdue tasks are visually highlighted. Reminders are stored and can be delivered as chatbot messages.

**Why this priority**: Due dates and reminders are fundamental for deadline-driven work. Users need to be reminded of approaching deadlines to avoid missing commitments.

**Independent Test**: A user creates a task with due date (tomorrow) and sets a reminder for "1 day before". The due date is displayed in the task card. When the reminder time arrives, the user is notified (via chatbot message or stored notification).

**Acceptance Scenarios**:

1. **Given** a user creates a task with a due date, **When** they save the task, **Then** the due date is displayed in the task card
2. **Given** a task's due date has passed, **When** the user views the task, **Then** it is marked as overdue (red indicator)
3. **Given** a user sets a reminder for a task, **When** the reminder time arrives, **Then** a notification is sent (logged in system, ready for delivery)
4. **Given** a user says "remind me to submit report on Friday at 3pm", **When** the chatbot processes the command, **Then** a task is created with due date Friday 3pm and reminder set

---

### Edge Cases

- **Tag deletion**: User deletes a tag → tasks retain tag reference; tag is removed from tag list but task tag field shows orphaned tag (UI should handle gracefully)
- **Recurring task modification**: User modifies a recurring task's title → only future instances use new title; past completed instances keep original title
- **Timezone handling**: User's task has due date "tomorrow at 9 AM" → system stores in UTC, displays in user's local timezone
- **Overdue recurring**: User marks an overdue recurring task complete → next instance is created with future due date (not overdue)
- **Filters with no results**: User applies filters that match zero tasks → UI shows "no tasks" message clearly; does not confuse with empty task list
- **Search with special characters**: User searches for "task @home" → search handles special characters gracefully (exact match or ignore non-alphanumeric)

---

## Requirements

### Functional Requirements

#### Intermediate Features (Priorities, Tags, Search, Filter, Sort)

- **FR-INT-1**: System MUST support three priority levels (Low, Medium, High) or a numeric scale (1-5); user can set/change priority for any task
- **FR-INT-2**: System MUST display task priority visually (color-coded badge, icon, or text) in task list and task detail views
- **FR-INT-3**: System MUST allow filtering tasks by priority; filtering by one priority shows only tasks with that priority
- **FR-INT-4**: System MUST allow sorting tasks by priority (high-to-low or low-to-high)
- **FR-INT-5**: System MUST support user-defined tags (free-text; no predefined list); users can create, edit, and delete tags
- **FR-INT-6**: System MUST allow applying multiple tags to a single task; tags are stored as a list/array
- **FR-INT-7**: System MUST display tags in task cards as colored pills or similar visual element
- **FR-INT-8**: System MUST allow filtering tasks by tag; filtering by one tag shows all tasks with that tag (OR logic if multiple tags selected)
- **FR-INT-9**: System MUST support full-text search on task title and description fields; search is case-insensitive and supports partial word matches
- **FR-INT-10**: System MUST display search results with matching tasks ordered by relevance (tasks with matches in title first, then description)
- **FR-INT-11**: System MUST support filtering by status (pending/incomplete, completed); showing only tasks in the selected status
- **FR-INT-12**: System MUST support filtering by due date range (overdue, today, this week, this month)
- **FR-INT-13**: System MUST support sorting by multiple criteria: created date (ascending/descending), due date, priority, title (alphabetical), status
- **FR-INT-14**: System MUST combine multiple filters with AND logic (all criteria must match); combine multiple tags with OR logic (any tag can match)
- **FR-INT-15**: System MUST persist all intermediate feature data in Neon PostgreSQL with proper schema and migrations
- **FR-INT-16**: System MUST enforce multi-user isolation (user_id filter) for all priority/tag/search/filter/sort operations

#### Advanced Features (Recurring Tasks, Due Dates & Reminders)

- **FR-ADV-1**: System MUST support recurring task schedules with rules: daily, weekly, monthly, yearly, or custom (every X days)
- **FR-ADV-2**: System MUST allow expressing recurrence rules in human-readable format (e.g., "every Monday", "every 2 weeks") or RRULE format
- **FR-ADV-3**: System MUST automatically create the next instance of a recurring task when the current instance is marked complete
- **FR-ADV-4**: System MUST calculate the next occurrence date based on the recurrence rule and current date/time
- **FR-ADV-5**: System MUST allow users to edit or delete a recurring task; deletion stops future instances; editing affects only future instances
- **FR-ADV-6**: System MUST support due dates with optional time component (date only or date + time)
- **FR-ADV-7**: System MUST store due dates in UTC internally; display in user's local timezone in UI
- **FR-ADV-8**: System MUST visually mark tasks as overdue if due date has passed and task is not completed (red highlighting, alert icon, or text)
- **FR-ADV-9**: System MUST support reminder offsets (e.g., "1 day before", "1 hour before", "at due time") relative to due date
- **FR-ADV-10**: System MUST store reminders with task; when reminder time arrives, system logs the reminder event (ready for delivery mechanism in future)
- **FR-ADV-11**: System MUST allow users to snooze reminders; snoozed reminders are rescheduled for later (e.g., 1 hour, 1 day)
- **FR-ADV-12**: System MUST support recurring task + reminder combination (e.g., daily standup with 1-day-before reminder)
- **FR-ADV-13**: System MUST persist all advanced feature data in Neon PostgreSQL with proper schema and migrations
- **FR-ADV-14**: System MUST enforce multi-user isolation (user_id filter) for all recurring task and reminder operations
- **FR-ADV-15**: System MUST handle edge cases: timezone changes, daylight saving time, leap years, modifying recurring task mid-series

#### Chatbot Integration

- **FR-CHAT-1**: System MUST extend MCP tools to support new task operations: create task with priority/tags/due date/recurrence, update task with these fields
- **FR-CHAT-2**: System MUST extend MCP tools' list_tasks function to support filters (priority, tag, due date, status) and sorting
- **FR-CHAT-3**: Chatbot MUST understand natural language commands for priorities (e.g., "add high priority task", "show pending high priority work tasks")
- **FR-CHAT-4**: Chatbot MUST understand natural language commands for tags (e.g., "tag this task as urgent", "show work tasks")
- **FR-CHAT-5**: Chatbot MUST understand search commands (e.g., "search for groceries", "find tasks with meeting")
- **FR-CHAT-6**: Chatbot MUST understand filter commands (e.g., "show pending tasks", "filter by work tag", "show high priority tasks")
- **FR-CHAT-7**: Chatbot MUST understand sort commands (e.g., "sort by priority", "show newest first", "order by due date")
- **FR-CHAT-8**: Chatbot MUST understand recurring task commands (e.g., "add daily standup task", "make this task weekly", "create a task every Monday")
- **FR-CHAT-9**: Chatbot MUST understand due date and reminder commands (e.g., "remind me to submit report on Friday at 3pm", "set due date for task 2 to tomorrow", "add a 1-day reminder to this task")
- **FR-CHAT-10**: Chatbot MUST handle ambiguity and ask for clarification when necessary (e.g., "which task?" if context is ambiguous)

---

### Key Entities

#### Extended Task Model

**Task** (extends Phase 2 model):
- `id`: UUID (primary key)
- `user_id`: UUID (foreign key to User; ensures multi-user isolation)
- `title`: String (required)
- `description`: String (optional, full-text searchable)
- `status`: Enum (pending, completed) — existing field
- `priority`: Enum (low, medium, high) or Integer (1-5) — **NEW**
- `tags`: Array of Strings or JSON field (e.g., ["work", "urgent"]) — **NEW**
- `due_date`: DateTime (nullable; stored in UTC) — **NEW**
- `recurrence_rule`: String (e.g., "FREQ=DAILY" or "daily") — **NEW**
- `reminder_offset`: Integer (minutes/hours/days before due date; e.g., 1440 for 1 day) — **NEW**
- `created_at`: DateTime (existing field)
- `updated_at`: DateTime (existing field)
- `completed_at`: DateTime (nullable; existing or new)

#### New Tables/Entities

**Tag** (optional; if normalized tag management):
- `id`: UUID (primary key)
- `user_id`: UUID (foreign key to User; tags are per-user)
- `name`: String (e.g., "work", "personal", "urgent")
- `color`: String (hex color for UI; e.g., "#FF5733") — optional
- `created_at`: DateTime

**TaskTag** (junction table for many-to-many relationship):
- `task_id`: UUID (foreign key to Task)
- `tag_id`: UUID (foreign key to Tag)
- Primary key: (task_id, tag_id)

**RecurrenceInstance** (optional; for complex recurring logic):
- `id`: UUID (primary key)
- `task_id`: UUID (foreign key to Task)
- `instance_date`: Date (the date this instance is scheduled for)
- `due_date`: DateTime (calculated due date for this instance)
- `completed_at`: DateTime (nullable; when instance was completed)
- `next_instance_created_at`: DateTime (nullable; when next instance was auto-created)

**Reminder** (optional; for persistent reminder tracking):
- `id`: UUID (primary key)
- `task_id`: UUID (foreign key to Task)
- `reminder_time`: DateTime (absolute time for reminder; calculated from due_date + offset)
- `reminder_type`: Enum (in-app, email, webhook, chatbot-message) — for future delivery
- `is_sent`: Boolean (default false; true after reminder is delivered)
- `snoozed_until`: DateTime (nullable; if snoozed, reminder is rescheduled for this time)
- `created_at`: DateTime

---

## Success Criteria

### Measurable Outcomes

#### Intermediate Features
- **SC-INT-1**: Users can create and prioritize tasks; task list displays priorities correctly with <100ms response time
- **SC-INT-2**: Filtering by priority returns correct results; 99.99% accuracy (no false negatives/positives)
- **SC-INT-3**: Sorting by priority reorders list correctly within 500ms
- **SC-INT-4**: Users can create custom tags; 50+ tags per user supported without performance degradation
- **SC-INT-5**: Tag filtering returns correct results; combining multiple tags shows union (OR logic) correctly
- **SC-INT-6**: Full-text search returns relevant results within 1 second (p95 latency)
- **SC-INT-7**: Search supports 100+ words/phrases without false negatives
- **SC-INT-8**: Combining filters (priority + tag + status) works correctly with AND logic
- **SC-INT-9**: Sorting works with any combination of criteria (date, priority, title, status)
- **SC-INT-10**: All intermediate features work for logged-in user only; multi-user isolation enforced

#### Advanced Features
- **SC-ADV-1**: Recurring tasks create next instance within 5 seconds of current instance completion
- **SC-ADV-2**: Recurring task calculation is accurate for daily, weekly, monthly, yearly, and custom schedules
- **SC-ADV-3**: Recurring tasks work correctly across timezone boundaries and daylight saving time transitions
- **SC-ADV-4**: Due dates are displayed in user's local timezone (no confusion with UTC storage)
- **SC-ADV-5**: Overdue highlighting appears correctly for tasks past due date and not completed
- **SC-ADV-6**: Reminders are triggered at correct time (within ±5 minutes of scheduled time)
- **SC-ADV-7**: Reminder system supports 99.9% delivery rate (no lost reminders)
- **SC-ADV-8**: Snoozed reminders are rescheduled correctly; users can snooze multiple times
- **SC-ADV-9**: Combining recurring + reminder works (e.g., daily task with 1-day-before reminder works correctly over multiple cycles)
- **SC-ADV-10**: All advanced features work for logged-in user only; multi-user isolation enforced

#### Chatbot Integration
- **SC-CHAT-1**: Chatbot understands priority/tag/search/filter/sort commands with 95%+ accuracy
- **SC-CHAT-2**: Chatbot understands recurring task commands and creates tasks with correct recurrence
- **SC-CHAT-3**: Chatbot understands due date/reminder commands and creates tasks with correct due dates and reminders
- **SC-CHAT-4**: Chatbot responses are natural and helpful (users report 90%+ satisfaction)
- **SC-CHAT-5**: Chatbot handles ambiguous commands by asking clarifying questions (not making silent assumptions)

---

## Constraints & Assumptions

### Assumptions

1. Phase 2 frontend (Next.js, Tailwind) and Phase 3 chatbot (ChatKit, MCP tools) are complete and functional
2. Phase 2 backend (FastAPI, SQLModel) is complete and functional
3. Neon PostgreSQL is available as external database; no local database setup required
4. Better Auth (JWT) authentication is already integrated; no auth changes needed
5. OpenAI Agents SDK and Cohere API are configured for chatbot; no AI model changes needed
6. Users understand that reminders are logged in system and can be delivered later (initial implementation may not include real-time push/email; future phase will add delivery mechanisms)
7. Tag management is simple initially (free-text tags; no predefined vocabulary needed)
8. Recurring task implementation uses simple rules (RRULE format or human-readable strings); complex recurrence edge cases can be handled iteratively
9. UI/UX decisions (color schemes, icon choices, filter UI layout) are made by Frontend Engineer based on Tailwind constraints and existing design system
10. Chatbot prompt and MCP tool updates are made by AI Agent Engineer based on existing patterns in Phase 3

### Constraints

1. **Scope**: Part A only — features only, no deployment, no Dapr, no Kafka, no CI/CD
2. **No Database Migration Tools**: Use Alembic (already integrated in Phase 2) for database schema changes
3. **No Breaking Changes to Phase 2-3**: New fields are additive; existing API endpoints remain backward-compatible
4. **Timezone Handling**: All due dates stored in UTC; display in user's timezone (timezone from user profile or browser)
5. **No Real-time Reminders (Phase A)**: Reminders are logged/stored; actual delivery (push, email, webhook) is Part B/C scope (Dapr bindings)
6. **Chatbot Constraints**: All commands must work with existing MCP tools and OpenAI Agents SDK; no new frameworks or models

---

## Acceptance Test Plan

| Test ID | Scenario | Steps | Expected Result |
|---------|----------|-------|-----------------|
| AT-INT-1 | Create high-priority task | User creates task, sets priority=high, saves | Task displays high-priority badge/color |
| AT-INT-2 | Filter by priority | User filters by priority=high | Only high-priority tasks shown |
| AT-INT-3 | Sort by priority | User sorts by priority (high→low) | Tasks reordered: high, medium, low |
| AT-INT-4 | Create and apply tags | User creates task, applies tags=[work, urgent] | Tags visible as colored pills |
| AT-INT-5 | Filter by tag | User filters by tag=work | Only tasks with work tag shown |
| AT-INT-6 | Full-text search | User searches for "budget" | Tasks with "budget" in title/description returned |
| AT-INT-7 | Combine filters | User filters status=incomplete AND priority=high AND tag=work | Only tasks matching all criteria shown |
| AT-INT-8 | Sort results | User applies sort=due_date to filtered results | Results sorted by due date correctly |
| AT-ADV-1 | Create recurring task | User creates daily standup task | Task marked as recurring; visible in task details |
| AT-ADV-2 | Auto-create next instance | User marks daily standup complete | Tomorrow's instance appears in task list |
| AT-ADV-3 | Set due date | User creates task, sets due_date=tomorrow | Due date displayed in task card |
| AT-ADV-4 | Overdue highlighting | User creates task with due_date=yesterday, status=incomplete | Task highlighted as overdue (red) |
| AT-ADV-5 | Set reminder | User creates task, sets reminder=1 day before due date | Reminder stored; system ready to deliver at reminder time |
| AT-ADV-6 | Chatbot priority command | User says "add high priority task write report" | Task created with title="write report", priority=high |
| AT-ADV-7 | Chatbot tag command | User says "show work tasks" | Tasks with tag=work displayed |
| AT-ADV-8 | Chatbot search command | User says "find tasks with meeting" | Tasks with "meeting" in title/description returned |
| AT-ADV-9 | Chatbot recurring command | User says "create a daily standup task" | Recurring task created with daily recurrence |
| AT-ADV-10 | Chatbot due date command | User says "remind me to submit report on Friday at 3pm" | Task created with due_date=Friday 3pm, reminder set |

---

## Out of Scope (for Part A)

The following are explicitly out of scope for this specification (they belong to Part B & C):

- **Cloud Deployment**: AKS, GKE, OKE, Kubernetes, Helm charts
- **Event-Driven Architecture**: Kafka topics, event publishing, event consumers
- **Dapr Integration**: Pub/Sub, State management, Bindings, Secrets, Service Invocation
- **CI/CD Pipeline**: GitHub Actions, automated deployment, container images
- **Real-time Reminders**: Push notifications, email, webhook delivery (stored only; delivery in future phase)
- **Monitoring & Logging**: Observability, alerting, metrics collection
- **Local Minikube Deployment**: Docker, docker-compose, Kubernetes on local machine
- **Advanced Reminder Scheduling**: Cron jobs, scheduled background tasks (Dapr bindings in Part B)

---

## Integration with Phase 2-3

### Reusing Existing Code

- **Frontend**: Extend existing Next.js Task form and task list components; reuse Tailwind styling and layout patterns
- **Backend**: Extend existing FastAPI endpoints for tasks; reuse SQLModel Task model, JWT authentication, user_id isolation pattern
- **Chatbot**: Extend existing MCP tools (add_task, update_task, list_tasks); extend existing ChatKit UI and agent prompts
- **Database**: Extend existing Neon PostgreSQL schema with new columns/tables; use Alembic for migrations

### API Contracts (Backward-Compatible)

**Task Endpoints** (existing, extend with new fields):
- `POST /api/{user_id}/tasks` — Create task (add priority, tags, due_date, recurrence_rule, reminder_offset fields)
- `GET /api/{user_id}/tasks` — List tasks (add query params: priority, tag, status, due_date_range, search, sort)
- `PATCH /api/{user_id}/tasks/{task_id}` — Update task (add priority, tags, due_date, recurrence_rule, reminder_offset)
- `DELETE /api/{user_id}/tasks/{task_id}` — Delete task (no changes)

**Chatbot MCP Tools** (existing, extend):
- `add_task(title, description, priority, tags, due_date, recurrence_rule, reminder_offset)` — Create task with new fields
- `update_task(task_id, title, description, priority, tags, due_date, recurrence_rule, reminder_offset)` — Update task
- `list_tasks(priority_filter, tag_filter, status_filter, due_date_range_filter, search_query, sort_by)` — List with filters and sorting
- `complete_task(task_id)` — Mark complete; if recurring, auto-create next instance

---

## Next Steps

1. **Clarifications** (if needed): Use `/sp.clarify` if requirements need refinement
2. **Architecture Planning**: Use `/sp.plan` to design database schema, API endpoints, UI components
3. **Task Breakdown**: Use `/sp.tasks` to create actionable implementation tasks
4. **Implementation**: Use `/sp.implement` to execute tasks

---

**Status**: Ready for planning phase
**Reviewed**: Phase 5 Constitution ✅
**Next Command**: `/sp.plan`
