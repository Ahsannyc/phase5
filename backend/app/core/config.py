"""Application configuration using pydantic-settings."""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    database_url: str = Field(..., alias="DATABASE_URL")
    better_auth_secret: str = Field(..., alias="BETTER_AUTH_SECRET")
    better_auth_url: str = Field(default="http://localhost:3000", alias="BETTER_AUTH_URL")

    # AI/ML Configuration
    cohere_api_key: str = Field(..., alias="COHERE_API_KEY")
    openai_api_key: str = Field(..., alias="OPENAI_API_KEY")
    mcp_server_port: int = Field(default=8001, alias="MCP_SERVER_PORT")

    class Config:
        """Configuration class."""
        env_file = ".env"
        case_sensitive = False


settings = Settings()