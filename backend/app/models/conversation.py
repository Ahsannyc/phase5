from datetime import datetime
from sqlmodel import SQLModel, Field
from typing import Optional


class Conversation(SQLModel, table=True):
    """Represents a conversation session between a user and the AI chatbot."""

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    title: Optional[str] = Field(default=None)  # Auto-generated from first message
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
