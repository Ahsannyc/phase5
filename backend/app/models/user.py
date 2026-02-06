"""User model definition."""

from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class UserBase(SQLModel):
    """Base user model."""
    email: str = Field(unique=True, index=True)
    name: Optional[str] = None


class User(UserBase, table=True):
    """User database model."""
    id: Optional[int] = Field(default=None, primary_key=True)
    password_hash: str
    created_at: datetime = Field(default_factory=datetime.now)


class UserCreate(UserBase):
    """User creation model."""
    password: str


class UserUpdate(SQLModel):
    """User update model."""
    email: Optional[str] = None
    name: Optional[str] = None
    password: Optional[str] = None


class UserRead(UserBase):
    """User response model."""
    id: int
    created_at: datetime