"""User CRUD operations."""

from sqlmodel import select, Session
from app.models.user import User, UserCreate
from app.core.security import get_password_hash
from typing import Optional


def create_user(db: Session, user_create: UserCreate) -> User:
    """Create a new user."""
    # Hash the password
    hashed_password = get_password_hash(user_create.password)

    # Create user object with hashed password
    db_user = User(
        email=user_create.email,
        name=user_create.name,
        password_hash=hashed_password
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get a user by email."""
    statement = select(User).where(User.email == email)
    user = db.exec(statement).first()
    return user


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Get a user by ID."""
    statement = select(User).where(User.id == user_id)
    user = db.exec(statement).first()
    return user