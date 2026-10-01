"""Tests for PlannerService business logic."""
import pytest
from study_planner.service import PlannerService


class TestPlannerService:
    """Test PlannerService core operations."""

    def test_service_initialization(self) -> None:
        """Test that service initializes with loaded data."""
        service = PlannerService()
        assert isinstance(service.tasks, list)
        assert isinstance(service.subjects, list)

    def test_add_task_valid(self) -> None:
        """Test adding a valid task."""
        service = PlannerService()
        initial_count = len(service.tasks)
        task = service.add_task("Test task", "2026-12-31")
        assert len(service.tasks) == initial_count + 1
        assert task.title == "Test task"
        assert task.due_date == "2026-12-31"

    def test_add_task_invalid_date(self) -> None:
        """Test that adding task with invalid date raises ValueError."""
        service = PlannerService()
        with pytest.raises(ValueError, match="Due date must use YYYY-MM-DD format"):
            service.add_task("Test", "invalid-date")

    def test_add_task_with_nonexistent_subject(self) -> None:
        """Test that adding task with nonexistent subject raises ValueError."""
        service = PlannerService()
        with pytest.raises(ValueError, match="subject ID does not exist"):
            service.add_task("Test", "2026-12-31", "nonexistent-subject")

    def test_complete_task(self) -> None:
        """Test completing a task."""
        service = PlannerService()
        service.add_task("Task to complete", "2026-12-31")
        initial_count = len(service.tasks)
        service.complete_task(initial_count - 1)
        assert len(service.tasks) == initial_count - 1

    def test_complete_task_invalid_index(self) -> None:
        """Test that completing invalid task index raises IndexError."""
        service = PlannerService()
        with pytest.raises(IndexError, match="Invalid task number"):
            service.complete_task(999)

    def test_clear_tasks(self) -> None:
        """Test clearing all tasks."""
        service = PlannerService()
        service.add_task("Task 1", "2026-12-31")
        service.add_task("Task 2", "2026-12-31")
        service.clear_tasks()
        assert len(service.tasks) == 0

    def test_add_subject(self) -> None:
        """Test adding a subject."""
        service = PlannerService()
        initial_count = len(service.subjects)
        subject = service.add_subject("test-subject", "Test Subject", "AQA")
        assert len(service.subjects) == initial_count + 1
        assert subject.id == "test-subject"
        assert subject.name == "Test Subject"

    def test_add_subject_invalid_name(self) -> None:
        """Test that adding subject without name raises ValueError."""
        service = PlannerService()
        with pytest.raises(ValueError, match="Subject ID and name are required"):
            service.add_subject("test", "", "AQA")

    def test_add_subject_duplicate_id(self) -> None:
        """Test that adding subject with duplicate ID raises ValueError."""
        service = PlannerService()
        service.add_subject("unique-id", "First Subject", "AQA")
        with pytest.raises(ValueError, match="subject ID already exists"):
            service.add_subject("unique-id", "Second Subject", "Edexcel")

    def test_tasks_sorted_by_due_date(self) -> None:
        """Test that tasks are sorted by due date."""
        service = PlannerService()
        service.clear_tasks()
        service.add_task("Task 3", "2026-12-31")
        service.add_task("Task 1", "2026-10-01")
        service.add_task("Task 2", "2026-11-15")
        
        dates = [task.due_date for task in service.tasks]
        assert dates == sorted(dates)
