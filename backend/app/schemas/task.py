"""Task schema definitions."""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TaskBase(BaseModel):
    """Base task schema."""
    title: str
    description: Optional[str] = None
    completed: bool = False


class TaskCreate(TaskBase):
    """Task creation schema."""
    pass


class TaskUpdate(BaseModel):
    """Task update schema."""
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None


class TaskToggle(BaseModel):
    """Task completion toggle schema."""
    completed: bool


class TaskResponse(TaskBase):
    """Task response schema."""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime