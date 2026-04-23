from functools import lru_cache
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ENV: str = "development"

    # Server
    DEBUG: bool = False 
    HOST: str = "0.0.0.0"
    PORT: int = Field(default=8000, ge=1, le=65535)
    
    # Blockchain
    BLOCKCHAIN_NODE_URL: str = "http://localhost:3000"
    BLOCKCHAIN_REQUEST_TIMEOUT: int = Field(default=30, ge=1, le=300)
    
    # Postgres
    DATABASE_URL: str = "postgresql+asyncpg://user:pass@localhost/blockkick"
    DATABASE_POOL_SIZE: int = Field(default=10, ge=1, le=50)
    DATABASE_MAX_OVERFLOW: int = Field(default=20, ge=0)
    
    # JWT
    JWT_SECRET: str = Field(..., min_length=16)
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Pydantic
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )
    
    @field_validator("BLOCKCHAIN_NODE_URL")
    @classmethod
    def validate_node_url(cls, v: str) -> str:
        if not v.startswith(("http://", "https://")):
            raise ValueError("BLOCKCHAIN_NODE_URL must start with http(s)://")
        return v.rstrip("/")
    
    @field_validator("DEBUG", mode="before")
    @classmethod
    def parse_debug(cls, v) -> bool:
        if isinstance(v, bool):
            return v
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes", "on")
        return bool(v)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings() # type: ignore[reportCallIssue]


settings = get_settings()
