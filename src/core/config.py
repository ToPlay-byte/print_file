from pathlib import Path

from pydantic import BaseModel

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).parent.parent.parent


class RedisSettings(BaseModel):
    """Configuration for Redis connection."""

    host: str = 'localhost'
    port: int = 6379
    db: int = 0


class CelerySettings(BaseModel):
    """Configuration for Celery."""

    broker: str = 'redis://localhost:6379/0'
    backend: str = 'redis://localhost:6379/0'
    task_serializer: str = "json"
    result_serializer: str = "json"


class Settings(BaseSettings):
    """Global application settings."""

    model_config = SettingsConfigDict(
        env_file=f'{BASE_DIR}/src/core/.env', env_nested_delimiter='__'
    )

    redis: RedisSettings = RedisSettings()
    celery: CelerySettings = CelerySettings()

    uploaded_files: Path = BASE_DIR / 'uploaded_files'


settings = Settings()
