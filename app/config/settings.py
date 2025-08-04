from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "FastAPI Expert API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Log
    LOG_FORMAT: str = "json"
    LOG_LEVEL: str = "INFO"


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()
