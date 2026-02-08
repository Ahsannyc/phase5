from datetime import datetime
from sqlmodel import SQLModel, Field
from typing import Optional


class Message(SQLModel, table=True):
    """Represents a message in a conversation with role and optional tool calls/responses."""

    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversation.id", index=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    role: str = Field(index=False)  # "user", "assistant", or "tool"
    content: str
    tool_calls: Optional[str] = Field(default=None)  # JSON serialized tool calls
    tool_responses: Optional[str] = Field(default=None)  # JSON serialized tool responses
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
