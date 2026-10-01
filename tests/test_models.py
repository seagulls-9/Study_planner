"""Tests for domain models (Task, Subject)."""
import pytest
from study_planner.models import Task, Subject


class TestTask:
    """Test Task dataclass validation and methods."""

    def test_task_creation_valid(self) -> None:
        """Test creating a valid task."""
        task = Task(due_date="2026-12-31", title="Complete project")
        assert task.title == "Complete project"
        assert task.due_date == "2026-12-31"
        assert task.subject_id == ""

    def test_task_title_cannot_be_empty(self) -> None:
        """Test that task title cannot be empty."""
        with pytest.raises(ValueError, match="Task title cannot be empty"):
            Task(due_date="2026-12-31", title="")

    def test_task_title_cannot_be_whitespace(self) -> None:
        """Test that task title cannot be only whitespace."""
        with pytest.raises(ValueError, match="Task title cannot be empty"):
            Task(due_date="2026-12-31", title="   ")

    def test_task_title_max_length(self) -> None:
        """Test that task title cannot exceed 200 characters."""
        long_title = "x" * 201
        with pytest.raises(ValueError, match="cannot exceed 200 characters"):
            Task(due_date="2026-12-31", title=long_title)

    def test_task_due_date_format_invalid(self) -> None:
        """Test that due date must be in YYYY-MM-DD format."""
        with pytest.raises(ValueError, match="Due date must use YYYY-MM-DD format"):
            Task(due_date="31/12/2026", title="Test")

    def test_task_with_subject(self) -> None:
        """Test creating a task with subject ID."""
        task = Task(due_date="2026-12-31", title="Math homework", subject_id="maths")
        assert task.subject_id == "maths"

    def test_task_to_dict(self) -> None:
        """Test converting task to dictionary."""
        task = Task(due_date="2026-12-31", title="Test task")
        task_dict = task.to_dict()
        assert task_dict["title"] == "Test task"
        assert task_dict["due_date"] == "2026-12-31"

    def test_task_from_dict(self) -> None:
        """Test creating task from dictionary."""
        data = {"due_date": "2026-12-31", "title": "Test task", "subject_id": ""}
        task = Task.from_dict(data)
        assert task.title == "Test task"
        assert task.due_date == "2026-12-31"


class TestSubject:
    """Test Subject dataclass."""

    def test_subject_creation_valid(self) -> None:
        """Test creating a valid subject."""
        subject = Subject(id="maths", name="Mathematics", exam_board="AQA")
        assert subject.id == "maths"
        assert subject.name == "Mathematics"
        assert subject.exam_board == "AQA"

    def test_subject_to_dict(self) -> None:
        """Test converting subject to dictionary."""
        subject = Subject(id="physics", name="Physics", exam_board="Edexcel")
        subject_dict = subject.to_dict()
        assert subject_dict["id"] == "physics"
        assert subject_dict["name"] == "Physics"

    def test_subject_from_dict(self) -> None:
        """Test creating subject from dictionary."""
        data = {
            "id": "chemistry",
            "name": "Chemistry",
            "exam_board": "OCR",
            "notes": "Important concepts",
            "topics": [],
        }
        subject = Subject.from_dict(data)
        assert subject.id == "chemistry"
        assert subject.name == "Chemistry"
