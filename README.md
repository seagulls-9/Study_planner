# Study Planner

A student study planner with two separate interfaces powered by one shared core.

## Run it

```bash
pip install -r requirements.txt
python -m study_planner.cli
python -m study_planner.study_planner_gui
```

The terminal and GUI versions use the same `tasks.json` and `subjects.json` files. The shared code demonstrates separation of concerns:

- `models.py` — validated domain models
- `storage.py` — atomic JSON persistence and migration of older task data
- `service.py` — business rules used by both interfaces
- `pmt_service.py` — PMT URL generation, parsing and retry logic
- `cli.py` — terminal interface
- `study_planner_gui.py` — CustomTkinter interface

## Quality features

The project includes type hints, dataclasses, validation, logging, atomic writes, network retries, and a clear separation between presentation and application logic. This makes it easier to test and extend than putting all behaviour inside the GUI callbacks.
