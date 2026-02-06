"""Authentication API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from app.database import get_async_session
from app.schemas.user import UserCreate, UserLogin, TokenResponse
from app.models.user import User
from app.crud.user import create_user, get_user_by_email
from app.core.security import verify_password, create_access_token
from sqlmodel import select
from datetime import timedelta
from typing import Any


auth_router = APIRouter()


@auth_router.post("/signup", response_model=TokenResponse, status_code=201)
async def signup(
    user_create: UserCreate,
    db: AsyncSession = Depends(get_async_session)
) -> Any:
    """Register a new user."""
    # Check if user already exists
    existing_user = await db.exec(select(User).where(User.email == user_create.email))
    if existing_user.first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create the user
    db_user = await db.run_sync(lambda session: create_user(session, user_create))

    # Create JWT token
    access_token_expires = timedelta(days=7)  # Token valid for 7 days
    access_token = create_access_token(
        data={"sub": str(db_user.id)},  # Convert to string for JWT compliance
        expires_delta=access_token_expires
    )

    # Return user info and token
    return TokenResponse(
        user=db_user,
        token=access_token
    )


@auth_router.post("/signin", response_model=TokenResponse)
async def signin(
    user_login: UserLogin,
    db: AsyncSession = Depends(get_async_session)
) -> Any:
    """Sign in an existing user."""
    # Find user by email
    db_user = await db.run_sync(lambda session: get_user_by_email(session, user_login.email))

    if not db_user or not verify_password(user_login.password, db_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create JWT token
    access_token_expires = timedelta(days=7)  # Token valid for 7 days
    access_token = create_access_token(
        data={"sub": str(db_user.id)},  # Convert to string for JWT compliance
        expires_delta=access_token_expires
    )

    # Return user info and token
    return TokenResponse(
        user=db_user,
        token=access_token
    )