"""Pytest configuration and shared fixtures."""
import pytest
from pathlib import Path
import json
from study_planner import config


@pytest.fixture(autouse=True)
def setup_test_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Set up isolated test environment with temporary files."""
    tasks_file = tmp_path / "tasks.json"
    subjects_file = tmp_path / "subjects.json"
    log_file = tmp_path / "test.log"
    
    # Initialize empty files
    tasks_file.write_text(json.dumps([]))
    subjects_file.write_text(json.dumps([]))
    
    # Patch config to use temporary files
    test_config = config.Config(
        base_dir=tmp_path,
        tasks_file=tasks_file,
        subjects_file=subjects_file,
        log_file=log_file,
        pmt_base_url="https://www.physicsandmathstutor.com",
        request_timeout=15,
        max_retries=3,
        date_format="%Y-%m-%d",
        max_title_length=200,
        max_notes_length=1000,
    )
    
    monkeypatch.setattr(config, "CONFIG", test_config)
