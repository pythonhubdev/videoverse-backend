import enum
import os
from functools import lru_cache


class LogLevel(str, enum.Enum):
	"""Possible log levels."""

	NOTSET = "NOTSET"
	DEBUG = "DEBUG"
	INFO = "INFO"
	WARNING = "WARNING"
	ERROR = "ERROR"
	FATAL = "FATAL"


class Environment(str, enum.Enum):
	"""Possible environments."""

	DEV = "DEV"
	PROD = "PROD"
	TEST = "TEST"


class Settings:
	"""
	Application settings.

	These parameters can be configured
	with environment variables.
	"""

	HOST: str = os.getenv("HOST", "0.0.0.0")
	PORT: int = int(os.getenv("PORT", 8000))
	WORKERS_COUNT: int = int(os.getenv("WORKERS_COUNT", 1))
	DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

	ENVIRONMENT: Environment = Environment[os.getenv("ENVIRONMENT", "DEV")]

	LOG_LEVEL: LogLevel = LogLevel.INFO

	DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./videoverse.db")


@lru_cache
def get_settings() -> Settings:
	"""Get application settings."""
	return Settings()


settings = Settings()
