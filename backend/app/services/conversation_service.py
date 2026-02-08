from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from datetime import datetime
from app.models.conversation import Conversation


class ConversationService:
    """Service for managing conversations."""

    @staticmethod
    async def create_conversation(db: AsyncSession, user_id: int, title: str = None) -> Conversation:
        """Create a new conversation for a user."""
        conversation = Conversation(user_id=user_id, title=title)
        db.add(conversation)
        await db.commit()
        await db.refresh(conversation)
        return conversation

    @staticmethod
    async def get_conversation(db: AsyncSession, conversation_id: int, user_id: int) -> Conversation:
        """Get a conversation by ID, ensuring user owns it."""
        stmt = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id,
        )
        return (await db.execute(stmt)).scalars().first()

    @staticmethod
    async def get_user_conversations(db: AsyncSession, user_id: int, limit: int = 50) -> list:
        """Get all conversations for a user."""
        stmt = (
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.created_at.desc())
            .limit(limit)
        )
        return (await db.execute(stmt)).scalars().all()

    @staticmethod
    async def update_conversation_title(db: AsyncSession, conversation_id: int, user_id: int, title: str) -> Conversation:
        """Update the title of a conversation."""
        conversation = await ConversationService.get_conversation(db, conversation_id, user_id)
        if conversation:
            conversation.title = title
            conversation.updated_at = datetime.utcnow()
            db.add(conversation)
            await db.commit()
            await db.refresh(conversation)
        return conversation
