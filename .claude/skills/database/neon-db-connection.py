"""
Async SQLModel + Neon PostgreSQL Connection Setup
Provides database engine and session dependency for FastAPI
"""

import os
from sqlmodel import create_engine, Session
from sqlmodel.ext.asyncio.session import AsyncSession
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import Depends

# Get database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/todo_db")

# Create async engine
engine = create_engine(DATABASE_URL, echo=False)

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Async session dependency for FastAPI routes
    Usage: async_session: AsyncSession = Depends(get_async_session)
    """
    async with AsyncSession(engine) as session:
        yield session

# Alternative sync session dependency (if needed)
def get_session() -> Generator[Session, None, None]:
    """
    Sync session dependency for FastAPI routes
    Usage: session: Session = Depends(get_session)
    """
    with Session(engine) as session:
        yield session