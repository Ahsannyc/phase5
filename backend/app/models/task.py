"""Task model definition."""

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime
from .user import User


class TaskBase(SQLModel):
    """Base task model."""
    title: str
    description: Optional[str] = None
    completed: bool = Field(default=False)


class Task(TaskBase, table=True):
    """Task database model."""
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    # Relationship with user
    user: User = Relationship()


class TaskCreate(TaskBase):
    """Task creation model."""
    pass


class TaskUpdate(SQLModel):
    """Task update model."""
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None


class TaskRead(TaskBase):
    """Task response model."""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime