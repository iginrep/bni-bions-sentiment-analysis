import os
from functools import lru_cache

from pydantic import BaseModel, Field


def _env(name: str, default: str) -> str:
    return os.getenv(name, default)


def _mongodb_database() -> str:
    return os.getenv("MONGODB_DATABASE", os.getenv("MONGODB_DB", "bni_bions_sentiment"))


class Settings(BaseModel):
    app_timezone: str = Field(default_factory=lambda: _env("APP_TIMEZONE", "Asia/Jakarta"))
    sentiment_method: str = Field(default_factory=lambda: _env("SENTIMENT_METHOD", "indobert"))
    mongodb_uri: str = Field(default_factory=lambda: _env("MONGODB_URI", "mongodb://localhost:27017"))
    mongodb_database: str = Field(default_factory=_mongodb_database)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
