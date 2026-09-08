from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
    database_url: str
    jwt_secret_key: str = Field(min_length=32)
    access_token_expire_minutes: int = Field(default=60, ge=1, le=1440)

    @field_validator("database_url")
    @classmethod
    def postgres_only(cls, value: str) -> str:
        if not value.startswith("postgresql+psycopg://"):
            raise ValueError("DATABASE_URL must use postgresql+psycopg://")
        return value

    @field_validator("jwt_secret_key")
    @classmethod
    def reject_placeholder(cls, value: str) -> str:
        if value.startswith("replace_"):
            raise ValueError("Generate JWT_SECRET_KEY with scripts/setup_env.py")
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
