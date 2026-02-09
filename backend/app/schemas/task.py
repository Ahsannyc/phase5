"""Task schema definitions with Phase 5 Part A extensions."""

from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime


class TaskBase(BaseModel):
    """Base task schema."""
    title: str
    description: Optional[str] = None
    completed: bool = False


class TaskCreate(TaskBase):
    """Task creation schema with Phase 5 Part A fields."""
    priority: str = "medium"
    tags: list[str] = []
    due_date: Optional[datetime] = None
    recurrence_rule: Optional[str] = None
    reminder_offset: Optional[int] = None

    @field_validator('priority')
    @classmethod
    def validate_priority(cls, v: str) -> str:
        """Validate priority is one of: low, medium, high."""
        if v not in ['low', 'medium', 'high']:
            raise ValueError('Priority must be one of: low, medium, high')
        return v

    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v: list[str]) -> list[str]:
        """Validate tags: max 20 tags, max 50 chars each."""
        if len(v) > 20:
            raise ValueError('Maximum 20 tags allowed')
        for tag in v:
            if not tag or len(tag) > 50:
                raise ValueError('Each tag must be 1-50 characters')
        return v

    @field_validator('reminder_offset')
    @classmethod
    def validate_reminder_offset(cls, v: Optional[int]) -> Optional[int]:
        """Validate reminder_offset is non-negative and reasonable (max 7 days)."""
        if v is not None:
            if v < 0:
                raise ValueError('Reminder offset must be non-negative')
            if v > 10080:  # 7 days * 24 hours
                raise ValueError('Reminder offset must be <= 10080 hours (7 days)')
        return v


class TaskUpdate(BaseModel):
    """Task update schema with Phase 5 Part A fields."""
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None
    priority: Optional[str] = None
    tags: Optional[list[str]] = None
    due_date: Optional[datetime] = None
    recurrence_rule: Optional[str] = None
    reminder_offset: Optional[int] = None

    @field_validator('priority')
    @classmethod
    def validate_priority(cls, v: Optional[str]) -> Optional[str]:
        """Validate priority if provided."""
        if v is not None and v not in ['low', 'medium', 'high']:
            raise ValueError('Priority must be one of: low, medium, high')
        return v

    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v: Optional[list[str]]) -> Optional[list[str]]:
        """Validate tags if provided."""
        if v is not None:
            if len(v) > 20:
                raise ValueError('Maximum 20 tags allowed')
            for tag in v:
                if not tag or len(tag) > 50:
                    raise ValueError('Each tag must be 1-50 characters')
        return v

    @field_validator('reminder_offset')
    @classmethod
    def validate_reminder_offset(cls, v: Optional[int]) -> Optional[int]:
        """Validate reminder_offset if provided."""
        if v is not None:
            if v < 0:
                raise ValueError('Reminder offset must be non-negative')
            if v > 10080:
                raise ValueError('Reminder offset must be <= 10080 hours (7 days)')
        return v


class TaskToggle(BaseModel):
    """Task completion toggle schema."""
    completed: bool


class TaskResponse(TaskBase):
    """Task response schema with Phase 5 Part A fields."""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    priority: str
    tags: list[str]
    due_date: Optional[datetime]
    recurrence_rule: Optional[str]
    reminder_offset: Optional[int]
    is_overdue: bool = False  # Computed property

    class Config:
        from_attributes = True