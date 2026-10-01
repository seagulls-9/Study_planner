# 📚 Study Planner

[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![CustomTkinter](https://img.shields.io/badge/UI-CustomTkinter-1f6feb)](https://github.com/TomSchimansky/CustomTkinter)

**Production-grade task management for students.** Track assignments by due date and subject. Keep data locally in readable JSON files—no account required.

Built with **clean architecture**: CLI and GUI interfaces share a type-safe, testable business logic core. Perfect for students and developers learning software design patterns.

## Why Study Planner?

✅ **Privacy-first** — Data stays local. No tracking, no accounts.  
✅ **Dual interfaces** — Use CLI or CustomTkinter GUI interchangeably.  
✅ **Clean code** — Separation of concerns, type hints, validation, atomic writes.  
✅ **Resilient** — Exponential backoff, crash-safe persistence, professional logging.  
✅ **Educational** — Learn production Python patterns in 600 lines.

## Quick start

```bash
git clone https://github.com/seagulls-9/Study_planner.git
cd Study_planner
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -e "."

# Desktop GUI
python -m study_planner.study_planner_gui

# Terminal
python -m study_planner.cli
```

Both interfaces share `tasks.json`, `subjects.json`, and `study_planner.log`.

## Features

- 📝 Add tasks with due dates and subject tags
- 📅 View tasks sorted by deadline with days-remaining
- ✅ Mark tasks complete
- 📖 Organize subjects by exam board
- 🌐 Fetch study materials from Physics & Maths Tutor
- 💾 Atomic writes (safe against crashes)
- 🔒 Type-safe throughout
- 📊 Rotating file logging

## Architecture

```
study_planner/
├── models.py              # Task, Subject (validated dataclasses)
├── service.py             # PlannerService (business logic core)
├── storage.py             # Atomic JSON persistence
├── pmt_service.py         # Physics & Maths Tutor integration
├── config.py              # Configuration & logging
├── cli.py                 # Terminal interface
└── study_planner_gui.py   # CustomTkinter GUI
```

Both UIs call `PlannerService`. This separation makes the core testable and leaves room for a REST API or mobile backend.

## Configuration

Optional environment variables:

```bash
PMT_BASE_URL=https://www.physicsandmathstutor.com
PMT_REQUEST_TIMEOUT=15
PMT_MAX_RETRIES=3
```

## Development

```bash
pip install -e ".[dev]"
ruff check .          # Lint
black --check .       # Format check
mypy study_planner/   # Type check
pytest                # Run tests
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

## What this demonstrates

```
✓ Separation of concerns (models, service, storage, UI)
✓ Type hints throughout (PEP 484)
✓ Data validation in __post_init__
✓ Atomic file writes
✓ Exponential backoff for resilience
✓ Centralized configuration
✓ Professional logging patterns
✓ Code organization for testability
✓ Dual-interface architecture
```

Universities and code reviewers notice this. It's **production-grade** not student-grade.

## License

MIT — see [LICENSE](LICENSE)

## Contributing

Bug reports, feature requests, and pull requests welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

**Built by [@seagulls-9](https://github.com/seagulls-9)**
