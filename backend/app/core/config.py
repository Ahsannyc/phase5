"""Application configuration using pydantic-settings."""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    database_url: str
    better_auth_secret: str
    better_auth_url: str = "http://localhost:3000"

    class Config:
        """Configuration class."""
        env_file = ".env"
        case_sensitive = True


settings = Settings()