# Study Planner

A small Python app for keeping track of school assignments and revision subjects. Add assignments with due dates, group them by subject and exam board, and use the desktop app to fetch revision-topic links from Physics & Maths Tutor (PMT). It has a CustomTkinter desktop interface and a command-line interface.

## Quick start

```bash
git clone https://github.com/seagulls-9/Study_planner.git
cd Study_planner
python -m venv .venv
```

Activate the environment, then install and run either interface:

```bash
# macOS/Linux
source .venv/bin/activate

# Windows PowerShell
.venv\Scripts\Activate.ps1

pip install -e .
python -m study_planner.study_planner_gui  # Desktop app
python -m study_planner.cli               # Command line
```

The app keeps `tasks.json`, `subjects.json`, and `study_planner.log` in the project directory. Both interfaces use the same files.

## What it does

- Add assignments with a title, due date, and optional subject.
- View assignments in due-date order and see how many days remain.
- Mark assignments complete or clear the task list.
- Add subjects with an exam board and notes.
- In the desktop app, fetch topic links for supported subjects and boards from PMT. The links are shown with the subject; the app does not download the revision materials.

## Data and PMT

Tasks and subjects are stored as readable JSON files in the project directory. The app writes changes to a temporary file and then replaces the existing file. If a data file is unreadable or contains invalid JSON, the app logs a warning and starts with an empty list for that file. Keep a backup if the data matters to you.

PMT topic fetching requires an internet connection and depends on the site's pages remaining compatible with the link parser. Requests use a timeout and retry failed attempts. If fetching fails, the subject remains saved, but its topic links may be empty. PMT content and availability are outside this project's control.

## Configuration

These environment variables are optional:

```text
PMT_BASE_URL=https://www.physicsandmathstutor.com
PMT_REQUEST_TIMEOUT=15
PMT_MAX_RETRIES=3
```

`PMT_MAX_RETRIES` sets the number of request attempts. The default timeout is 15 seconds and the default is three attempts.

## Development

```bash
pip install -e ".[dev]"
pytest
ruff check .
black --check .
mypy study_planner/
```

## License

MIT. See [LICENSE](LICENSE).
