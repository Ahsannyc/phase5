"""Task model definition."""

from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy import JSON
from typing import Optional
from datetime import datetime, timedelta
from enum import Enum
from .user import User


class TaskStatus(str, Enum):
    """Task status enum."""
    PENDING = "pending"
    COMPLETED = "completed"


class TaskPriority(str, Enum):
    """Task priority enum."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TaskBase(SQLModel):
    """Base task model."""
    title: str
    description: Optional[str] = None
    completed: bool = Field(default=False)


class Task(TaskBase, table=True):
    """Task database model with Phase 5 Part A extensions."""
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    # Phase 5 Part A - Intermediate Features
    priority: str = Field(default="medium", index=True)  # low, medium, high
    tags: list[str] = Field(default=[], sa_column=Column(JSON))  # JSON array of tags

    # Phase 5 Part A - Advanced Features
    due_date: Optional[datetime] = Field(None, index=True)  # UTC timezone
    recurrence_rule: Optional[str] = Field(None, index=True)  # "daily", "weekly:monday", etc.
    reminder_offset: Optional[int] = None  # Hours before due_date to remind

    # Relationship with user
    user: User = Relationship()

    @property
    def is_overdue(self) -> bool:
        """Check if task is overdue (due_date < now AND status != completed)."""
        if self.due_date and not self.completed:
            return self.due_date < datetime.utcnow()
        return False

    @property
    def reminder_datetime(self) -> Optional[datetime]:
        """Calculate when reminder should trigger (due_date - reminder_offset hours)."""
        if self.due_date and self.reminder_offset:
            return self.due_date - timedelta(hours=self.reminder_offset)
        return None


class TaskCreate(TaskBase):
    """Task creation model."""
    priority: str = "medium"
    tags: list[str] = []
    due_date: Optional[datetime] = None
    recurrence_rule: Optional[str] = None
    reminder_offset: Optional[int] = None


class TaskUpdate(SQLModel):
    """Task update model."""
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None
    priority: Optional[str] = None
    tags: Optional[list[str]] = None
    due_date: Optional[datetime] = None
    recurrence_rule: Optional[str] = None
    reminder_offset: Optional[int] = None


class TaskRead(TaskBase):
    """Task response model."""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    priority: str
    tags: list[str]
    due_date: Optional[datetime]
    recurrence_rule: Optional[str]
    reminder_offset: Optional[int]
    is_overdue: bool