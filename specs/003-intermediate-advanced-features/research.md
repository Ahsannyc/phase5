# Research: Phase 5 Part A – Intermediate & Advanced Features

**Feature**: Phase 5 Part A – Intermediate & Advanced Todo Features
**Branch**: `003-intermediate-advanced-features`
**Date**: 2026-02-09
**Stage**: Phase 0 Research Complete ✅

---

## Overview

This document captures Phase 0 research findings for all technical decisions required to implement Phase 5 Part A features. All unknowns have been resolved; no blocking dependencies remain.

---

## Research Questions & Decisions

### 1. Priority Field Implementation (Database)

**Question**: Use enum (low/medium/high) or numeric scale (1-5)?

**Decision**: Enum string ("low", "medium", "high")

**Rationale**:
- User stories use human-readable priorities ("high priority", "urgent")
- Semantic labels are easier for chatbot NLP (can parse "urgent" → priority="high")
- More intuitive in UI (dropdowns with labels > numeric scale)
- Aligns with industry standard (Jira, GitHub, Asana all use semantic priorities)

**Alternatives Considered**:
- Numeric scale (1-5): More flexible but less semantic; harder for chatbot NLP
- Boolean flags (High/Low): Insufficient granularity; doesn't capture "medium"
- String-only (free-text): Too flexible; breaks filtering/sorting

**Validation**: Priority must be one of "low", "medium", "high" (Pydantic enum)

---

### 2. Tag Storage (Database)

**Question**: Normalized table (Tag + TaskTag junction) or JSON array in Task?

**Decision**: JSON array in Task (denormalized)

**Rationale**:
- MVP simplicity: tags stored as JSONB array; no joins needed
- Sufficient for Phase 5 scope: typical users have <50 tags
- Faster read performance for common operation (list all tasks with tag filtering)
- Aligns with Phase 2-3 pattern (minimal schema complexity)
- Easy to migrate to normalized schema later if needed (data is simple)

**Alternatives Considered**:
- Normalized schema (Tag table + TaskTag junction): Better at scale (10M+ tasks); adds complexity
- JSONB with full-text search: Overkill for MVP; can add in Part B/C if needed
- Separate tags column per priority: Inflexible; violates 1NF

**Validation**: Tags must be array of non-empty strings; max 20 tags; max 50 chars each

**Migration Path**: If performance degrades (e.g., >1M tasks), normalize to:
```sql
CREATE TABLE tag (
  id UUID PRIMARY KEY,
  user_id UUID FK,
  name VARCHAR(50) UNIQUE,
  created_at TIMESTAMP
);

CREATE TABLE task_tag (
  task_id UUID FK,
  tag_id UUID FK,
  PRIMARY KEY (task_id, tag_id)
);
```

---

### 3. Recurrence Rule Format (Database)

**Question**: Use RRULE format (RFC 5545) or simplified strings?

**Decision**: Simplified strings initially; RRULE support added later

**Rationale**:
- Simplicity: "daily", "weekly:monday", "monthly:15" are human-readable and easy to parse
- Sufficient for 80% of use cases (daily, weekly, monthly, yearly)
- Easier for chatbot NLP ("repeat daily" → recurrence_rule="daily")
- Custom complex rules deferred to Part B/C (when scheduler/Dapr involved)
- Database size: simplified strings much smaller than full RRULE objects

**Format Specification**:
| Pattern | Meaning | Example |
|---------|---------|---------|
| `daily` | Every day | "daily" |
| `weekly:<day>` | Every week on specific day(s) | "weekly:monday", "weekly:mon,wed,fri" |
| `monthly:<day>` | Every month on specific day | "monthly:15" (15th of month), "monthly:last" (last day) |
| `yearly:<month>-<day>` | Every year on specific date | "yearly:march-15" |
| `custom:every-<n>-days` | Every N days | "custom:every-3-days" |

**Alternatives Considered**:
- Full RRULE (RFC 5545): Powerful but complex; harder for NLP; overkill for MVP
- Cron format: Familiar to developers but harder for end-users
- Database-agnostic DSL: Proprietary; harder to debug

**Validation**: Recurrence_rule must match one of above patterns; stored as VARCHAR(255)

**Future Enhancement** (Part B/C):
```python
# Convert to/from RFC 5545 RRULE for advanced scheduling
simplified = "weekly:monday"
rrule = "RRULE:FREQ=WEEKLY;BYDAY=MO"
```

---

### 4. Due Date & Reminder Storage (Database)

**Question**: Store reminder as absolute datetime or offset from due_date?

**Decision**: Store `reminder_offset` as integer (hours); calculate absolute datetime on-demand

**Rationale**:
- Offset survives timezone changes: if user's timezone changes, reminder still fires at correct local time
- Simpler to adjust: user can update offset without recalculating absolute times
- Source of truth: due_date is the primary field; offset is derived
- Stateless: no background scheduler needed for Phase 5 (can add in Part B/C via Dapr)

**Example**:
```python
# User sets: due_date=2026-02-15 15:00:00 UTC, reminder_offset=24 hours
reminder_datetime = due_date - timedelta(hours=24)  # 2026-02-14 15:00:00 UTC

# If user's timezone is US/Eastern (UTC-5):
# Display: Due date Feb 15 at 10am local; Remind Feb 14 at 10am local
# Backend always works in UTC
```

**Alternatives Considered**:
- Absolute datetime: Brittle across timezone changes; redundant with due_date
- Relative description ("1 day before"): Harder to query; requires parsing

**Validation**: Reminder_offset must be non-negative integer; reasonable max 10080 (7 days)

---

### 5. Search Implementation (Backend)

**Question**: Use PostgreSQL full-text search (FTS) or simple ILIKE?

**Decision**: ILIKE for Phase 5 MVP; full-text search (FTS) deferred to Part B/C

**Rationale**:
- 80/20 rule: ILIKE covers 80% of searches; FTS adds complexity without proportional benefit
- Performance: ILIKE on indexed columns is fast enough for <100k tasks per user
- Simplicity: one-liner query; no configuration needed
- Future-proof: can add trigram GIN index or full-text search index later

**Example**:
```sql
-- ILIKE (MVP)
SELECT * FROM task
WHERE user_id = $1
  AND (title ILIKE $2 OR description ILIKE $2)
ORDER BY created_at DESC;

-- Full-text search (Part B/C)
SELECT * FROM task
WHERE user_id = $1
  AND (to_tsvector('english', title || ' ' || description) @@ plainto_tsquery('english', $2))
ORDER BY created_at DESC;
```

**Alternatives Considered**:
- Full-text search: More powerful but requires additional index/configuration
- Regex search: Slower; can cause performance issues
- Elasticsearch: Overkill for Phase 5; adds operational complexity

**Migration Path**: Add full-text search in Part B/C if search latency exceeds 500ms

---

### 6. Filter Combination Logic (Backend)

**Question**: Should multiple filters combine with AND or OR?

**Decision**: AND for all criteria (status AND priority AND tag AND due_date range)

**Rationale**:
- More intuitive for users: "Show pending high-priority work tasks" means ALL criteria must match
- Predictable behavior: narrowing results, not broadening them
- Aligns with user expectations: users want to focus, not see more results

**Example**:
```python
# User applies: status=pending, priority=high, tag="work"
# Result: only tasks that are PENDING AND priority=high AND have tag "work"

# If no matching tasks: show "no tasks found" message
```

**Alternatives Considered**:
- OR: Would return pending tasks OR high-priority tasks OR work tasks; too broad
- Configurable: Adds UI complexity; confusing for users

---

### 7. Recurring Task Auto-Creation (Backend)

**Question**: Should next instance auto-create on completion or on schedule?

**Decision**: Auto-create on completion (synchronous, no scheduler needed)

**Rationale**:
- Simpler implementation: no background job / async worker needed
- More user-friendly: task disappears and reappears immediately when marked complete
- Stateless: backend remains stateless; no scheduler persistence needed
- Sufficient for Phase 5: MVP doesn't require scheduled generation

**Example**:
```python
# User marks "daily standup" (created today) as complete
# Backend:
#   1. Update current task status = COMPLETED
#   2. Immediately create new task (copy fields)
#   3. Calculate next due_date (today + 1 day)
#   4. Return both old and new task states

# Result: next "daily standup" appears tomorrow in task list
```

**Alternatives Considered**:
- Scheduled creation: Would require Dapr Binding (cron) or background worker; more complex
- Manual creation: Doesn't feel automatic; poor UX

**Future Enhancement** (Part B/C): Use Dapr Bindings (cron) to pre-generate recurring instances for performance optimization

---

### 8. Timezone Handling (Backend + Frontend)

**Question**: How to handle user timezone across frontend and backend?

**Decision**: Store all datetimes in UTC (backend); display in user's local timezone (frontend)

**Rationale**:
- Standard pattern: all databases store UTC; applications convert for display
- Browser provides timezone: JavaScript `Date` object uses local timezone automatically
- Prevents bugs: no confusion about which timezone a datetime refers to
- Scalable: supports users across all timezones without special handling

**Implementation**:
```javascript
// Frontend (TypeScript)
const dueDate = new Date("2026-02-15T15:00:00Z");  // UTC from API
const localString = dueDate.toLocaleString();       // Displayed in browser's timezone

// Backend (Python)
from datetime import datetime, timezone
due_date = datetime.now(timezone.utc)  # Store as UTC
```

**Alternatives Considered**:
- Server stores user's timezone: Adds complexity; still need to convert on backend
- All calculations in UTC: Works but less user-friendly

**Testing**: DST transitions (spring forward, fall back) are handled correctly

---

### 9. Overdue Detection (Backend + Frontend)

**Question**: How to calculate and display overdue status?

**Decision**: Overdue = due_date < now AND status = PENDING

**Rationale**:
- Simple boolean: due_date < utcnow() is straightforward
- Respects status: completed tasks are never overdue
- Database-backed: can index for fast queries
- UI-friendly: single property to check for styling

**Implementation**:
```python
# Backend (computed property)
@property
def is_overdue(self) -> bool:
    if self.due_date and self.status == TaskStatus.PENDING:
        return self.due_date < datetime.utcnow()
    return False

# Frontend (conditional styling)
{task.is_overdue && <span className="text-red-600">{task.due_date}</span>}
```

**Display**: Overdue tasks shown in red; visual indicator (⚠️) if needed

---

### 10. Reminder Notification System (Phase 5 MVP)

**Question**: How to deliver reminders in Phase 5 (before Dapr/Kafka)?

**Decision**: Store reminder_offset; calculate trigger time on-demand; display in chatbot (no scheduler in Phase 5)

**Rationale**:
- MVP scope: Phase 5 Part A doesn't require active notifications
- Storage ready: reminder_offset field stores reminder timing
- Future-ready: Part B/C can add Dapr Bindings (cron) for active delivery
- Sufficient for testing: chatbot can check "is reminder due?" and display message

**Implementation** (Phase 5):
```python
# Chatbot query: "What reminders do I have?"
# Backend:
#   1. Find all tasks where due_date - reminder_offset <= now
#   2. Filter by status = PENDING
#   3. Return list to chatbot for display

# Chatbot displays: "You have 2 reminders: task X due tomorrow at 3pm, task Y due in 2 hours"
```

**Future Enhancement** (Part B/C):
```yaml
# Dapr Binding (cron) - Part B/C
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: reminder-cron
spec:
  type: bindings.cron
  metadata:
  - name: schedule
    value: '@every 1m'  # Check every minute
  - name: handler
    value: checkReminders  # Dapr will call /checkReminders endpoint
```

---

## Unknowns Resolved ✅

| Unknown | Resolution | Status |
|---------|-----------|--------|
| Priority representation | Enum (low/medium/high) | ✅ RESOLVED |
| Tag storage | JSON array in Task | ✅ RESOLVED |
| Recurrence format | Simplified strings | ✅ RESOLVED |
| Reminder storage | Offset from due_date | ✅ RESOLVED |
| Search performance | ILIKE with index | ✅ RESOLVED |
| Filter logic | AND combination | ✅ RESOLVED |
| Auto-create trigger | On completion (sync) | ✅ RESOLVED |
| Timezone approach | UTC + local conversion | ✅ RESOLVED |
| Overdue calculation | due_date < now AND pending | ✅ RESOLVED |
| Reminder notifications | Phase 5: stored; Part B/C: active delivery | ✅ RESOLVED |

---

## Dependencies & Constraints

### External Dependencies (All Existing)
- **Database**: Neon PostgreSQL (existing from Phase 2)
- **Backend**: FastAPI, SQLModel, Alembic (existing)
- **Frontend**: Next.js, React, Tailwind (existing)
- **Chatbot**: OpenAI Agents SDK, MCP tools (existing from Phase 3)

### No New External Libraries
All Phase 5 Part A features can be implemented with existing stack.

### Breaking Changes
None. All changes are backward-compatible additions.

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| Tag performance (large arrays) | Low | Medium | Monitor array size; migrate to normalized schema if >100k tasks per user |
| Timezone bugs (DST) | Medium | Medium | Test with dates around DST transitions; use timezone-aware datetimes |
| Recurring task edge cases (leap years) | Low | Low | Use standard datetime math; handle edge cases iteratively |
| Chatbot NLP ambiguity ("work") | Medium | Medium | Train agent with examples; ask for clarification when ambiguous |
| Breaking Phase 2-3 queries | Low | High | All new fields nullable with safe defaults; existing queries unaffected |

---

## Conclusion

All Phase 0 research questions have been resolved. Technical decisions are documented and justified. No blocking unknowns remain.

**Status**: ✅ **Ready for Phase 1 Design & Phase 2 Implementation**

---

## Next Steps (Phase 1 Design)

1. ✅ Data model defined (data-model.md)
2. ✅ API contracts defined (plan.md)
3. ✅ MCP tool signatures defined (plan.md)
4. ✅ Frontend components planned (plan.md)
5. ⏭️ **Generate tasks.md** (Phase 2: implementation tasks)
6. ⏭️ **Implementation begins** (Phase 3: agents execute tasks)

