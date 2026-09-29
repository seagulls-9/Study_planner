"""Shared application configuration."""
from dataclasses import dataclass
from pathlib import Path
import logging
import os
from logging.handlers import RotatingFileHandler


@dataclass(frozen=True)
class Config:
    """Central settings used by both the CLI and GUI applications."""
    base_dir: Path = Path(__file__).resolve().parent.parent
    tasks_file: Path = Path(__file__).resolve().parent.parent / "tasks.json"
    subjects_file: Path = Path(__file__).resolve().parent.parent / "subjects.json"
    pmt_base_url: str = os.getenv("PMT_BASE_URL", "https://www.physicsandmathstutor.com")
    request_timeout: int = int(os.getenv("PMT_REQUEST_TIMEOUT", "15"))
    max_retries: int = int(os.getenv("PMT_MAX_RETRIES", "3"))
    date_format: str = "%Y-%m-%d"
    max_title_length: int = 200
    max_notes_length: int = 1000
    log_file: Path = Path(__file__).resolve().parent.parent / "study_planner.log"


CONFIG = Config()


def get_logger(name: str) -> logging.Logger:
    """Return a consistently configured rotating logger."""
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    handler = RotatingFileHandler(CONFIG.log_file, maxBytes=2_000_000, backupCount=3)
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
    logger.addHandler(handler)
    return logger
