# Contributing to Study Planner

Thank you for your interest in contributing. We welcome bug reports, feature requests, documentation improvements, and code contributions.

## Development setup

```bash
git clone https://github.com/YOUR_USERNAME/Study_planner.git
cd Study_planner
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -e ".[dev]"
```

## Running the app

```bash
# GUI
python -m study_planner.study_planner_gui

# CLI
python -m study_planner.cli
```

## Code style and checks

Before submitting a pull request:

```bash
ruff check .          # Linting
black .               # Formatting
mypy study_planner/   # Type checking
pytest                # Tests
```

## Architecture

Keep presentation code thin:
- `cli.py` and `study_planner_gui.py` — UI only
- `service.py` — Business logic and validation
- `models.py` — Domain model validation
- `storage.py` — Persistence layer
- `pmt_service.py` — External API integration

Changes to business logic go in `service.py`, `models.py`, or `storage.py` so both CLI and GUI benefit.

## Tests

Add tests for new features or bug fixes:

```bash
pytest                # Run all tests
pytest --cov          # Coverage report
pytest -v             # Verbose output
```

## Reporting issues

Include:
- Clear description of the problem
- Steps to reproduce
- Expected vs. actual behavior
- Python version and OS
- Which interface (CLI or GUI)

## Pull requests

1. Create a branch from `main`
2. Make your changes
3. Run tests and checks
4. Write a clear commit message
5. Open a pull request

We'll review and provide feedback.
