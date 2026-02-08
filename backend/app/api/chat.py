"""Chat API endpoints for AI chatbot."""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session, select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.database import get_async_session
from app.api.deps import get_current_user
from app.models.conversation import Conversation
from app.models.message import Message
from app.services.conversation_service import ConversationService
from app.services.message_service import MessageService
from app.agent.agent_runner import AgentRunner
from app.mcp.tools import TodoTools
from typing import Optional, Any, List
import json


class ChatMessage(BaseModel):
    """Request body for chat message."""
    content: str
    conversation_id: Optional[int] = None


class ChatResponse(BaseModel):
    """Response model for chat."""
    conversation_id: int
    message_id: int
    content: str
    role: str


class ConversationSummary(BaseModel):
    """Summary of a conversation."""
    id: int
    title: Optional[str] = None
    created_at: str


chat_router = APIRouter()


@chat_router.post("/send", response_model=ChatResponse)
async def send_message(
    request: ChatMessage,
    current_user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
) -> Any:
    """Send a message to the chatbot and get AI response with tool execution."""

    try:
        # Create or get conversation
        if request.conversation_id:
            stmt = select(Conversation).where(
                Conversation.id == request.conversation_id,
                Conversation.user_id == current_user_id,
            )
            conversation = (await db.execute(stmt)).scalars().first()
            if not conversation:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Conversation not found"
                )
        else:
            conversation = Conversation(user_id=current_user_id)
            db.add(conversation)
            await db.commit()
            await db.refresh(conversation)

        # Save user message
        user_msg = Message(
            conversation_id=conversation.id,
            user_id=current_user_id,
            role="user",
            content=request.content
        )
        db.add(user_msg)
        await db.commit()
        await db.refresh(user_msg)

        # Get conversation history (last 10 messages)
        stmt = (
            select(Message)
            .where(
                Message.conversation_id == conversation.id,
                Message.user_id == current_user_id,
            )
            .order_by(Message.created_at)
            .limit(10)
        )
        history_msgs = (await db.execute(stmt)).scalars().all()

        # Format history for agent
        messages = [
            {"role": m.role, "content": m.content}
            for m in history_msgs[:-1]  # Exclude the message we just added
        ]

        # Process with agent and tools
        try:
            agent = AgentRunner()
            tools = TodoTools(db)

            # Get agent response (this will handle tool calling)
            response_data = await agent.process_message(
                request.content,
                messages,
                current_user_id,
                tools
            )
            assistant_response = response_data["content"]
        except Exception as agent_error:
            # Fallback if agent fails
            assistant_response = f"I understand you want to: {request.content}. Please ensure your COHERE_API_KEY is set in environment variables."

        # Save assistant message
        assistant_msg = Message(
            conversation_id=conversation.id,
            user_id=current_user_id,
            role="assistant",
            content=assistant_response,
            tool_calls=None
        )
        db.add(assistant_msg)
        await db.commit()
        await db.refresh(assistant_msg)

        return {
            "conversation_id": conversation.id,
            "message_id": assistant_msg.id,
            "content": assistant_msg.content,
            "role": "assistant"
        }

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing message: {str(e)}"
        )


@chat_router.get("/conversations", response_model=List[ConversationSummary])
async def list_conversations(
    current_user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
) -> Any:
    """List all conversations for the current user."""

    stmt = (
        select(Conversation)
        .where(Conversation.user_id == current_user_id)
        .order_by(Conversation.created_at.desc())
        .limit(50)
    )
    conversations = (await db.execute(stmt)).scalars().all()

    return [
        {
            "id": c.id,
            "title": c.title,
            "created_at": c.created_at.isoformat()
        }
        for c in conversations
    ]


@chat_router.get("/conversations/{conversation_id}/messages")
async def get_conversation_messages(
    conversation_id: int,
    current_user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
) -> Any:
    """Get all messages in a conversation."""

    # Verify conversation exists and belongs to user
    conv_stmt = select(Conversation).where(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user_id,
    )
    conversation = (await db.execute(conv_stmt)).scalars().first()
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    # Get messages
    msg_stmt = (
        select(Message)
        .where(
            Message.conversation_id == conversation_id,
            Message.user_id == current_user_id,
        )
        .order_by(Message.created_at)
    )
    messages = (await db.execute(msg_stmt)).scalars().all()

    return [
        {
            "id": m.id,
            "role": m.role,
            "content": m.content,
            "created_at": m.created_at.isoformat(),
            "tool_calls": json.loads(m.tool_calls) if m.tool_calls else None,
        }
        for m in messages
    ]
