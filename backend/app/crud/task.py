"""Task CRUD operations."""

from sqlmodel import select, Session
from app.models.task import Task, TaskCreate, TaskUpdate
from typing import List, Optional


def create_task(db: Session, task_create: TaskCreate, user_id: int) -> Task:
    """Create a new task for a user."""
    db_task = Task.from_orm(task_create)
    db_task.user_id = user_id
    db.add(db_task)
    db.commit()
    db.refresh(db_task)

    return db_task


def get_tasks_by_user(db: Session, user_id: int) -> List[Task]:
    """Get all tasks for a user."""
    statement = select(Task).where(Task.user_id == user_id)
    tasks = db.exec(statement).all()
    return tasks


def get_task_by_id_and_user(db: Session, task_id: int, user_id: int) -> Optional[Task]:
    """Get a specific task by ID and user ID."""
    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    task = db.exec(statement).first()
    return task


def update_task(db: Session, task_id: int, task_update: TaskUpdate, user_id: int) -> Optional[Task]:
    """Update a task for a user."""
    db_task = get_task_by_id_and_user(db, task_id, user_id)
    if not db_task:
        return None

    # Update only the fields that are provided
    update_data = task_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_task, field, value)

    db.add(db_task)
    db.commit()
    db.refresh(db_task)

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
    """Toggle the completion status of a task."""
    db_task = get_task_by_id_and_user(db, task_id, user_id)
    if not db_task:
        return None

    db_task.completed = completed
    db.add(db_task)
    db.commit()
    db.refresh(db_task)

    return db_task