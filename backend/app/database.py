"""Database engine and session configuration."""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession as SQLModelAsyncSession
from app.core.config import settings
import os


# Create async engine
# Replace postgresql:// with postgresql+asyncpg:// for async support
database_url = settings.database_url.replace("postgresql://", "postgresql+asyncpg://")
engine = create_async_engine(database_url)

# Create async session maker
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=SQLModelAsyncSession,
    expire_on_commit=False,
)


async def get_async_session():
    """Dependency to get async session."""
    async with AsyncSessionLocal() as session:
        yield session