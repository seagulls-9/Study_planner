"""Atomic JSON persistence shared by the CLI and GUI."""
import json
from pathlib import Path
from typing import Any
from .config import get_logger

LOGGER = get_logger(__name__)


def load_json(path: Path, default: Any) -> Any:
    try:
        with path.open(encoding="utf-8") as file:
            return json.load(file)
    except (OSError, json.JSONDecodeError):
        LOGGER.warning("Could not load %s; using defaults", path)
        return default


def save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)
        file.write("\n")
    temporary.replace(path)


def load_tasks(path: Path) -> list[dict[str, Any]]:
    raw = load_json(path, [])
    result = []
    for item in raw if isinstance(raw, list) else []:
        if isinstance(item, dict):
            try:
                result.append(item)
            except (TypeError, ValueError):
                LOGGER.warning("Ignoring invalid task: %r", item)
        elif isinstance(item, str):
            parts = item.split(" - ", 1)
            if len(parts) == 2:
                result.append({"due_date": parts[0], "title": parts[1]})
    return result


def load_subjects(path: Path) -> list[dict[str, Any]]:
    raw = load_json(path, [])
    return [item for item in raw if isinstance(item, dict)] if isinstance(raw, list) else []
