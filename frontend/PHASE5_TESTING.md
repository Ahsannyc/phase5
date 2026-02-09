# Phase 5 Part A - Frontend Testing Guide

## Implementation Summary

All Phase 5 Part A frontend components have been implemented:

### Components Updated/Created

1. **lib/types.ts** - Extended with Phase 5 Part A fields
   - `priority`: 'low' | 'medium' | 'high'
   - `tags`: string[]
   - `due_date`: string
   - `recurrence_rule`: string
   - `reminder_offset`: number
   - `is_overdue`: boolean

2. **components/ui/TaskForm.tsx** - EXTENDED
   - Priority dropdown (Low/Medium/High)
   - Tags input with chip display (max 20 tags)
   - Due date datetime-local input
   - Recurrence rule dropdown (14 options)
   - Reminder offset number input (0-10080 hours)

3. **components/ui/TaskCard.tsx** - EXTENDED
   - Priority badge with color coding (red/yellow/green)
   - Tags display as purple pills
   - Due date display with overdue warning
   - Recurrence indicator
   - Overdue border highlighting (red)

4. **components/ui/TaskListControls.tsx** - NEW
   - Search input
   - Priority filter dropdown
   - Status filter dropdown (pending/completed)
   - Sort dropdown (8 options)
   - Clear filters button

5. **components/ui/TaskList.tsx** - EXTENDED
   - Integrated TaskListControls
   - Filter state management
   - Empty state with filter message

6. **lib/api.ts** - EXTENDED
   - getTasks() now accepts filter parameters
   - Properly maps to backend API (tag, sort)

7. **app/(protected)/page.tsx** - EXTENDED
   - Filter state management
   - Auto-refetch on filter change
   - Passes filters to TaskList

## Manual Testing Checklist

### 1. Create Task with All Fields
```
1. Navigate to /tasks/new
2. Fill in:
   - Title: "Test Phase 5 Task"
   - Description: "Testing all new fields"
   - Priority: High
   - Tags: Add "urgent", "testing", "phase5"
   - Due Date: Tomorrow at 2:00 PM
   - Recurrence: daily
   - Reminder: 24 hours before
3. Click "Create Task"
4. Verify task appears in dashboard with all fields displayed
```

### 2. Test Priority Display
```
1. Create 3 tasks with different priorities
2. Verify color coding:
   - High = Red badge
   - Medium = Yellow badge
   - Low = Green badge
```

### 3. Test Tags
```
1. Create task with multiple tags
2. Verify tags appear as purple pills on card
3. Try to add 21st tag (should be blocked)
4. Verify each tag can be removed in form
```

### 4. Test Due Date & Overdue
```
1. Create task with due date in the past
2. Verify "⚠️ OVERDUE" badge appears
3. Verify red border on task card
4. Verify due date shows in red
5. Mark task complete
6. Verify overdue indicator disappears
```

### 5. Test Recurrence Display
```
1. Create task with recurrence_rule: "daily"
2. Verify "🔄 Recurs: daily" appears on card
3. Try other recurrence rules
4. Mark recurring task complete (backend should create next instance)
```

### 6. Test Search Filter
```
1. Create tasks: "Buy milk", "Sell stocks", "Call mom"
2. In search box, type "milk"
3. Verify only "Buy milk" shows
4. Clear filter
5. Verify all tasks return
```

### 7. Test Priority Filter
```
1. Create tasks with mixed priorities
2. Select "High" in priority filter
3. Verify only high priority tasks show
4. Change to "Low"
5. Verify only low priority tasks show
```

### 8. Test Status Filter
```
1. Create some tasks, complete some
2. Select "Pending" in status filter
3. Verify only incomplete tasks show
4. Select "Completed"
5. Verify only completed tasks show
```

### 9. Test Sort
```
1. Create tasks with different due dates
2. Select "Due Date (Earliest)" in sort
3. Verify tasks sorted by due date ascending
4. Select "Priority (High First)"
5. Verify high priority tasks appear first
6. Select "Title (A-Z)"
7. Verify alphabetical order
```

### 10. Test Edit Task
```
1. Click edit on existing task
2. Verify all Phase 5 fields populated correctly
3. Change priority from Medium to High
4. Add new tag
5. Update due date
6. Save
7. Verify all changes reflected
```

### 11. Test Multi-User Isolation
```
1. Sign in as User A, create tasks with all fields
2. Sign out
3. Sign in as User B
4. Verify User A's tasks NOT visible
5. Create tasks as User B
6. Sign out and back in as User A
7. Verify User B's tasks NOT visible
```

### 12. Test Reminder Offset Validation
```
1. Try to enter reminder_offset = -1 (should fail)
2. Try to enter reminder_offset = 20000 (should fail, max 10080)
3. Enter reminder_offset = 24 (should succeed)
```

## API Endpoints Used

```
GET /api/tasks?search=text&priority=high&status=pending&sort=created_at
POST /api/tasks (with Phase 5 fields)
PUT /api/tasks/{id} (with Phase 5 fields)
DELETE /api/tasks/{id}
PATCH /api/tasks/{id}/complete
```

## Expected Behavior

### Priority
- Default: "medium"
- Options: low, medium, high
- Displayed as colored badge

### Tags
- Max 20 tags per task
- Each tag max 50 characters
- Displayed as chips/pills
- Can be added/removed in form

### Due Date
- Optional datetime field
- Displayed in localized format
- Overdue indicator if past and not completed

### Recurrence
- Optional string field
- Format: "daily", "weekly:monday", "monthly:15", "yearly:march-15"
- Displayed with 🔄 icon

### Reminder
- Optional integer (hours before due date)
- Range: 0-10080 (7 days)
- Sent by backend (not frontend responsibility)

## Known Issues/Limitations

1. Frontend does not implement reminder sending (backend responsibility)
2. Recurring task next instance creation handled by backend
3. Filters are client-initiated but processed server-side
4. No real-time updates (requires manual refresh or filter change)

## Files Modified

```
frontend/lib/types.ts
frontend/lib/api.ts
frontend/components/ui/TaskForm.tsx
frontend/components/ui/TaskCard.tsx
frontend/components/ui/TaskList.tsx
frontend/components/ui/TaskListControls.tsx (NEW)
frontend/app/(protected)/page.tsx
```

## Next Steps

1. Start frontend dev server: `npm run dev` in frontend/
2. Ensure backend is running on port 8000
3. Test all features manually
4. Run automated tests if available
5. Deploy to staging for user acceptance testing
