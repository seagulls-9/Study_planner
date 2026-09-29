# Study Planner

A task management application for students built with clean architecture and type safety. Two separate interfaces (CLI and GUI) share a robust business logic core.

## Overview

Study Planner solves a real problem: tracking assignments across multiple subjects with deadline awareness. More importantly, it demonstrates production-quality Python practices: separation of concerns, type hints, validation, error handling, and testable code.

## Quick Start

```bash
pip install -r requirements.txt
python -m study_planner.cli                    # Terminal interface
python -m study_planner.study_planner_gui      # GUI interface (CustomTkinter)
```

Both versions use the same `tasks.json` and `subjects.json` files.

## Architecture

The project separates presentation from business logic:

```
study_planner/
├── config.py              # Configuration and logging setup
├── models.py              # Task and Subject (dataclasses with validation)
├── storage.py             # Atomic JSON persistence
├── pmt_service.py         # Physics & Maths Tutor integration with retries
├── service.py             # PlannerService (business logic, no UI dependencies)
├── cli.py                 # Terminal interface
└── study_planner_gui.py   # CustomTkinter GUI interface
```

Both UIs use the same `PlannerService`, avoiding code duplication and making the core logic easy to test.

## Key Features

- Add tasks with due dates and subject tags
- View tasks sorted by deadline with days-remaining calculation
- Mark tasks complete
- Organize by subject with exam board tracking
- Fetch study materials from Physics and Maths Tutor with retry logic
- Atomic file writes (safe against crashes)
- Rotating file logging

## Technical Decisions

### Type Hints (PEP 484)
All functions and methods have type annotations for clarity and IDE support:
```python
def add_task(self, title: str, due_date: str, subject_id: str = "") -> Task:
```

### Data Validation
Tasks and subjects validate input in `__post_init__`:
```python
def __post_init__(self) -> None:
    if not self.title.strip():
        raise ValueError("Task title cannot be empty.")
    datetime.strptime(self.due_date, "%Y-%m-%d")
```

### Atomic Writes
File saves use a temporary file + atomic replace pattern to prevent corruption:
```python
temporary = path.with_suffix(path.suffix + ".tmp")
# ... write to temporary ...
temporary.replace(path)  # Atomic on most filesystems
```

### Retry Logic
Network calls to PMT use exponential backoff:
```python
for attempt in range(CONFIG.max_retries):
    try:
        return fetch_topics_from_pmt()
    except (HTTPError, URLError):
        if attempt + 1 < CONFIG.max_retries:
            sleep(2 ** attempt)
```

### Centralized Configuration
Settings live in `config.py` and can be overridden via environment variables:
```python
pmt_base_url: str = os.getenv("PMT_BASE_URL", "https://www.physicsandmathstutor.com")
request_timeout: int = int(os.getenv("PMT_REQUEST_TIMEOUT", "15"))
```

## Design Rationale

By separating models, business logic, and presentation:

- **Testability**: Core logic can be tested without mocking UI frameworks
- **Maintainability**: A bug fix in `service.py` fixes both CLI and GUI
- **Extensibility**: Adding a REST API or database backend requires only new storage/UI layers
- **Clarity**: Each module has a single, clear responsibility

This structure scales from student projects to production applications.

## What This Demonstrates

- Clean architecture and separation of concerns
- Type safety and runtime validation
- Error resilience and graceful degradation
- Professional logging practices
- Defensive programming patterns
- Code organization for testability and maintainability

## Tech Stack

- Python 3.8+
- CustomTkinter (modern GUI)
- Built-in logging with rotation
- JSON persistence
- HTML parsing for web scraping

## Future Enhancements

- Unit tests for `service.py` and `models.py`
- REST API layer using the existing service
- SQLite backend (swap `storage.py`)
- Database migrations
- Task priorities and categories

---

Built by [@seagulls-9](https://github.com/seagulls-9)
