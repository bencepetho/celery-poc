import logging
import sys
from functools import lru_cache

from dotenv import find_dotenv
from pydantic import BaseSettings

from app.constants import LOGGER_FORMAT, LOGGER_DEBUG_FORMAT


def get_log_level(level: int | str) -> int:
    print(f"Getting log level for {level}")
    if isinstance(level, int):
        return level

    try:
        return getattr(logging, level)

    except AttributeError as exc:
        raise ValueError(f"Incorrect log level: {level}") from exc


class Settings(BaseSettings):
    CELERY_BROKER: str = "redis://redis:6379"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379"

    LOGGER_NAME: str = "celery-poc"
    LOGGER_LEVEL: int | str = logging.INFO
    LOGGER_FORMAT: str = (
        LOGGER_DEBUG_FORMAT
        if get_log_level(LOGGER_LEVEL) < logging.INFO
        else LOGGER_FORMAT
    )

    class Config:
        case_sensitive = True
        env_prefix = "POC_"
        env_file = find_dotenv(".env")
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    print("Got settings")
    return Settings()


@lru_cache()
def get_app_logger() -> logging.Logger:
    settings = get_settings()

    _logger = logging.getLogger(settings.LOGGER_NAME)

    _logger.setLevel(settings.LOGGER_LEVEL)
    _logger.propagate = False

    formatter = logging.Formatter(settings.LOGGER_FORMAT)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    _logger.addHandler(handler)

    # Intercept uvicorn logs
    uvicorn_logger = logging.getLogger("uvicorn")
    uvicorn_logger.handlers = _logger.handlers

    gunicorn_logger = logging.getLogger("uvicorn.access")
    gunicorn_logger.handlers = _logger.handlers

    print("Logger configured")

    return _logger
