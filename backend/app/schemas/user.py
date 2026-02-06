"""User schema definitions."""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """Base user schema."""
    email: str
    name: Optional[str] = None


class UserCreate(UserBase):
    """User creation schema."""
    password: str


class UserLogin(BaseModel):
    """User login schema."""
    email: str
    password: str


class UserResponse(UserBase):
    """User response schema."""
    id: int
    created_at: datetime


class UserWithToken(UserResponse):
    """User response with token."""
    token: str


class TokenResponse(BaseModel):
    """Token response schema."""
    user: UserResponse
    token: str