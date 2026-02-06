"""API dependencies."""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.database import get_async_session
from app.core.security import verify_token
from sqlmodel.ext.asyncio.session import AsyncSession


security = HTTPBearer()


async def get_db_session():
    """Get database session dependency."""
    async for session in get_async_session():
        yield session


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db_session)
):
    """Get current user from JWT token."""
    token = credentials.credentials
    token_data = verify_token(token)

    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # We could fetch user details from the database if needed
    # For now, just return the user_id from the token
    return token_data.user_id