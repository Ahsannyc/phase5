from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from datetime import datetime
from app.models.message import Message
import json


class MessageService:
    """Service for managing messages in conversations."""

    @staticmethod
    async def create_message(
        db: AsyncSession,
        conversation_id: int,
        user_id: int,
        role: str,
        content: str,
        tool_calls: dict = None,
        tool_responses: dict = None,
    ) -> Message:
        """Create a new message in a conversation."""
        message = Message(
            conversation_id=conversation_id,
            user_id=user_id,
            role=role,
            content=content,
            tool_calls=json.dumps(tool_calls) if tool_calls else None,
            tool_responses=json.dumps(tool_responses) if tool_responses else None,
        )
        db.add(message)
        await db.commit()
        await db.refresh(message)
        return message

    @staticmethod
    async def get_conversation_messages(db: AsyncSession, conversation_id: int, user_id: int, limit: int = 100) -> list:
        """Get all messages in a conversation, ensuring user owns it."""
        stmt = (
            select(Message)
            .where(
                Message.conversation_id == conversation_id,
                Message.user_id == user_id,
            )
            .order_by(Message.created_at)
            .limit(limit)
        )
        return (await db.execute(stmt)).scalars().all()

    @staticmethod
    async def get_message(db: AsyncSession, message_id: int, user_id: int) -> Message:
        """Get a message by ID, ensuring user owns it."""
        stmt = select(Message).where(
            Message.id == message_id,
            Message.user_id == user_id,
        )
        return (await db.execute(stmt)).scalars().first()

    @staticmethod
    async def update_message_content(db: AsyncSession, message_id: int, user_id: int, content: str) -> Message:
        """Update message content (used for assistant responses)."""
        message = await MessageService.get_message(db, message_id, user_id)
        if message:
            message.content = content
            db.add(message)
            await db.commit()
            await db.refresh(message)
        return message
