"""Business operations used by both front ends."""
from datetime import datetime
from .config import CONFIG
from .models import Subject, Task
from .pmt_service import make_id
from .storage import load_json, load_subjects, load_tasks, save_json


class PlannerService:
    """Application service containing rules, validation and persistence."""
    def __init__(self) -> None:
        self.tasks = [Task.from_dict(x) for x in load_tasks(CONFIG.tasks_file)]
        self.subjects = [Subject.from_dict(x) for x in load_subjects(CONFIG.subjects_file)]
        self.sort_tasks()

    def sort_tasks(self) -> None:
        self.tasks.sort(key=lambda task: task.due_date)

    def save(self) -> None:
        save_json(CONFIG.tasks_file, [task.to_dict() for task in self.tasks]); save_json(CONFIG.subjects_file, [subject.to_dict() for subject in self.subjects])

    def add_task(self, title: str, due_date: str, subject_id: str = "") -> Task:
        subject_id = make_id(subject_id) if subject_id else ""
        if subject_id and not any(s.id == subject_id for s in self.subjects): raise ValueError("That subject ID does not exist.")
        task = Task(due_date, title, subject_id); self.tasks.append(task); self.sort_tasks(); self.save(); return task

    def complete_task(self, index: int) -> None:
        if not 0 <= index < len(self.tasks): raise IndexError("Invalid task number.")
        self.tasks.pop(index); self.save()

    def clear_tasks(self) -> None:
        self.tasks.clear(); self.save()

    def add_subject(self, raw_id: str, name: str, board: str, notes: str = "", links: list[str] | None = None, topics: list[dict[str, str]] | None = None, pmt_url: str = "") -> Subject:
        subject_id = make_id(raw_id)
        if not subject_id or not name.strip(): raise ValueError("Subject ID and name are required.")
        if any(s.id == subject_id for s in self.subjects): raise ValueError("That subject ID already exists.")
        subject = Subject(subject_id, name.strip(), board.strip(), notes.strip(), links or [], topics or [], pmt_url); self.subjects.append(subject); self.save(); return subject
