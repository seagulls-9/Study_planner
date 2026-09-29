"""
Configuration management for Study Planner application.

Supports environment-based configuration with defaults.
"""

from dataclasses import dataclass
from pathlib import Path
import logging
from typing import Optional
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()


@dataclass
class Config:
    """Centralized configuration for Study Planner."""

    # Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    TASKS_FILE: Path = DATA_DIR / "tasks.json"
    SUBJECTS_FILE: Path = DATA_DIR / "subjects.json"
    LOG_DIR: Path = BASE_DIR / "logs"
    LOG_FILE: Path = LOG_DIR / "study_planner.log"

    # PMT (Physics and Maths Tutor) API
    PMT_BASE_URL: str = os.getenv("PMT_BASE_URL", "https://www.physicsandmathstutor.com")
    PMT_REQUEST_TIMEOUT: int = int(os.getenv("PMT_REQUEST_TIMEOUT", "15"))
    PMT_MAX_RETRIES: int = int(os.getenv("PMT_MAX_RETRIES", "3"))
    PMT_RETRY_BACKOFF: float = float(os.getenv("PMT_RETRY_BACKOFF", "2.0"))

    # UI Configuration
    WINDOW_WIDTH: int = 900
    WINDOW_HEIGHT: int = 700
    WINDOW_MIN_WIDTH: int = 750
    WINDOW_MIN_HEIGHT: int = 550
    APPEARANCE_MODE: str = os.getenv("APPEARANCE_MODE", "dark")
    COLOR_THEME: str = os.getenv("COLOR_THEME", "blue")

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_MAX_BYTES: int = 10_485_760  # 10MB
    LOG_BACKUP_COUNT: int = 5

    # Validation
    MAX_TITLE_LENGTH: int = 200
    MAX_NOTES_LENGTH: int = 1000
    DATE_FORMAT: str = "%Y-%m-%d"
    TASK_SORT_BY: str = os.getenv("TASK_SORT_BY", "due_date")  # or "created_at"

    def __post_init__(self) -> None:
        """Ensure required directories exist."""
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.LOG_DIR.mkdir(parents=True, exist_ok=True)


# Global config instance
config = Config()


def setup_logging(name: str) -> logging.Logger:
    """
    Configure logging for the application.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Configured logger instance
    """
    from logging.handlers import RotatingFileHandler

    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, config.LOG_LEVEL))

    # Create formatter
    formatter = logging.Formatter(config.LOG_FORMAT)

    # File handler with rotation
    file_handler = RotatingFileHandler(
        config.LOG_FILE,
        maxBytes=config.LOG_MAX_BYTES,
        backupCount=config.LOG_BACKUP_COUNT,
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console handler (only if not already added)
    if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger
