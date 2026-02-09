"""Task CRUD operations with Phase 5 Part A extensions."""

from sqlmodel import select, Session, or_, and_, col
from app.models.task import Task, TaskCreate, TaskUpdate
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy import func


def create_task(db: Session, task_create: TaskCreate, user_id: int) -> Task:
    """Create a new task for a user with Phase 5 Part A fields."""
    task_data = task_create.model_dump()
    task_data['user_id'] = user_id
    db_task = Task(**task_data)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)

    return db_task


def get_tasks_by_user(
    db: Session,
    user_id: int,
    priority: Optional[str] = None,
    tags: Optional[List[str]] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    due_date_range: Optional[str] = None,
    sort_by: str = "created_at",
    page: int = 1,
    page_size: int = 20
) -> List[Task]:
    """Get tasks for a user with optional filters and sorting."""
    statement = select(Task).where(Task.user_id == user_id)

    # Apply priority filter
    if priority:
        statement = statement.where(Task.priority == priority)

    # Apply tags filter (OR logic: any of the tags match)
    if tags:
        # PostgreSQL JSON contains operator for array matching
        for tag in tags:
            statement = statement.where(func.jsonb_exists(Task.tags, tag))

    # Apply status filter
    if status:
        if status == "pending":
            statement = statement.where(Task.completed == False)
        elif status == "completed":
            statement = statement.where(Task.completed == True)
        elif status == "overdue":
            statement = statement.where(
                and_(
                    Task.due_date < datetime.utcnow(),
                    Task.completed == False
                )
            )

    # Apply search filter (ILIKE on title and description)
    if search:
        search_pattern = f"%{search}%"
        statement = statement.where(
            or_(
                Task.title.ilike(search_pattern),
                Task.description.ilike(search_pattern)
            )
        )

    # Apply due_date_range filter
    if due_date_range:
        now = datetime.utcnow()
        if due_date_range == "today":
            start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = start_of_day + timedelta(days=1)
            statement = statement.where(
                and_(
                    Task.due_date >= start_of_day,
                    Task.due_date < end_of_day
                )
            )
        elif due_date_range == "week":
            end_of_week = now + timedelta(days=7)
            statement = statement.where(
                and_(
                    Task.due_date >= now,
                    Task.due_date < end_of_week
                )
            )
        elif due_date_range == "month":
            end_of_month = now + timedelta(days=30)
            statement = statement.where(
                and_(
                    Task.due_date >= now,
                    Task.due_date < end_of_month
                )
            )
        elif due_date_range == "overdue":
            statement = statement.where(
                and_(
                    Task.due_date < now,
                    Task.completed == False
                )
            )

    # Apply sorting
    if sort_by.startswith("-"):
        # Descending order
        field = sort_by[1:]
        statement = statement.order_by(col(getattr(Task, field)).desc())
    else:
        # Ascending order
        statement = statement.order_by(col(getattr(Task, sort_by)))

    # Apply pagination
    offset = (page - 1) * page_size
    statement = statement.offset(offset).limit(page_size)

    tasks = db.exec(statement).all()
    return list(tasks)


def get_task_by_id_and_user(db: Session, task_id: int, user_id: int) -> Optional[Task]:
    """Get a specific task by ID and user ID."""
    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    task = db.exec(statement).first()
    return task


def update_task(db: Session, task_id: int, task_update: TaskUpdate, user_id: int) -> Optional[Task]:
    """Update a task for a user; auto-creates next instance if recurring and completed."""
    db_task = get_task_by_id_and_user(db, task_id, user_id)
    if not db_task:
        return None

    # Store original recurrence_rule and due_date before update
    original_recurrence = db_task.recurrence_rule
    original_due_date = db_task.due_date

    # Update only the fields that are provided
    update_data = task_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_task, field, value)

    # Update timestamp
    db_task.updated_at = datetime.utcnow()

    db.add(db_task)
    db.commit()
    db.refresh(db_task)

    # Auto-create next instance if task is recurring and just marked complete
    if db_task.completed and original_recurrence:
        next_task = _create_next_recurring_instance(
            db, db_task, original_recurrence, original_due_date, user_id
        )

    return db_task


def delete_task(db: Session, task_id: int, user_id: int) -> bool:
    """Delete a task for a user."""
    db_task = get_task_by_id_and_user(db, task_id, user_id)
    if not db_task:
        return False

    db.delete(db_task)
    db.commit()

    return True


def toggle_task_completion(db: Session, task_id: int, completed: bool, user_id: int) -> Optional[Task]:
    """Toggle the completion status of a task; auto-creates next instance if recurring."""
    db_task = get_task_by_id_and_user(db, task_id, user_id)
    if not db_task:
        return None

    db_task.completed = completed
    if completed:
        db_task.updated_at = datetime.utcnow()

        # Auto-create next instance if recurring
        if db_task.recurrence_rule:
            _create_next_recurring_instance(
                db, db_task, db_task.recurrence_rule, db_task.due_date, user_id
            )

    db.add(db_task)
    db.commit()
    db.refresh(db_task)

    return db_task


def _create_next_recurring_instance(
    db: Session,
    original_task: Task,
    recurrence_rule: str,
    original_due_date: Optional[datetime],
    user_id: int
) -> Task:
    """Create next instance of a recurring task."""
    # Calculate next due date based on recurrence rule
    next_due_date = _calculate_next_due_date(recurrence_rule, original_due_date)

    # Create new task instance
    next_task_data = {
        "title": original_task.title,
        "description": original_task.description,
        "priority": original_task.priority,
        "tags": original_task.tags,
        "due_date": next_due_date,
        "recurrence_rule": recurrence_rule,
        "reminder_offset": original_task.reminder_offset,
        "completed": False,
        "user_id": user_id
    }

    next_task = Task(**next_task_data)
    db.add(next_task)
    db.commit()
    db.refresh(next_task)

    return next_task


def _calculate_next_due_date(recurrence_rule: str, current_due_date: Optional[datetime]) -> datetime:
    """Calculate next due date based on recurrence rule."""
    now = datetime.utcnow()
    base_date = current_due_date if current_due_date else now

    if recurrence_rule == "daily":
        return base_date + timedelta(days=1)
    elif recurrence_rule.startswith("weekly"):
        # Examples: "weekly:monday", "weekly:mon,wed,fri"
        return base_date + timedelta(weeks=1)
    elif recurrence_rule.startswith("monthly"):
        # Examples: "monthly:15", "monthly:last"
        # Simplified: add 30 days (more complex logic can be added later)
        return base_date + timedelta(days=30)
    elif recurrence_rule.startswith("yearly"):
        # Examples: "yearly:march-15"
        return base_date + timedelta(days=365)
    elif recurrence_rule.startswith("custom"):
        # Example: "custom:every-3-days"
        parts = recurrence_rule.split(":")
        if len(parts) == 2 and parts[1].startswith("every-"):
            days = int(parts[1].replace("every-", "").replace("-days", ""))
            return base_date + timedelta(days=days)

    # Default: daily
    return base_date + timedelta(days=1)