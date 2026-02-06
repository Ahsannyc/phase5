"""
FastAPI JWT Authentication Middleware
Verifies JWT tokens and extracts user_id from the token
Requires BETTER_AUTH_SECRET environment variable
"""

import os
from datetime import datetime
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from pydantic import BaseModel

# Initialize security scheme
security = HTTPBearer()

class UserPayload(BaseModel):
    """Structure of the user payload in JWT token"""
    user_id: str
    exp: int

def verify_jwt_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserPayload:
    """
    JWT verification dependency
    Usage: current_user: UserPayload = Depends(verify_jwt_token)

    Raises HTTPException if token is invalid
    """
    token = credentials.credentials

    # Get secret from environment
    secret = os.getenv("BETTER_AUTH_SECRET")
    if not secret:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="JWT secret not configured"
        )

    try:
        # Decode the token
        payload = jwt.decode(token, secret, algorithms=["HS256"])

        # Validate payload structure
        user_payload = UserPayload(**payload)

        # Check if token is expired
        if user_payload.exp < datetime.utcnow().timestamp():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )

        return user_payload

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )