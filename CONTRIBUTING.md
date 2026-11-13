# Contributing

For a local development setup, clone the repository, create and activate a virtual environment, then install the development dependencies:

```bash
git clone https://github.com/seagulls-9/Study_planner.git
cd Study_planner
python -m venv .venv
source .venv/bin/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

Before opening a pull request, run the tests and checks:

```bash
pytest
ruff check .
black --check .
mypy study_planner/
```

For bug reports, include what you were doing, what happened, and your Python version and operating system. For changes to tasks, subjects, or PMT fetching, please include or update tests where practical.
