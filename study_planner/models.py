"""Validated domain models shared by both interfaces."""
from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from typing import Any


@dataclass
class Task:
    due_date: str
    title: str
    subject_id: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))

    def __post_init__(self) -> None:
        self.title = self.title.strip()
        if not self.title:
            raise ValueError("Task title cannot be empty.")
        if len(self.title) > 200:
            raise ValueError("Task title cannot exceed 200 characters.")
        try:
            datetime.strptime(self.due_date, "%Y-%m-%d")
        except ValueError as error:
            raise ValueError("Due date must use YYYY-MM-DD format.") from error

    @property
    def days_remaining(self) -> int:
        return (date.fromisoformat(self.due_date) - date.today()).days

    def display_status(self) -> str:
        days = self.days_remaining
        if days < 0:
            return f"OVERDUE by {abs(days)} days"
        if days == 0:
            return "Due TODAY"
        return f"{days} days left"

    def to_dict(self) -> dict[str, str]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Task":
        return cls(str(data.get("due_date", "")), str(data.get("title", "")), str(data.get("subject_id", "")), str(data.get("created_at", "")) or datetime.now().isoformat(timespec="seconds"))


@dataclass
class Subject:
    id: str
    name: str
    exam_board: str = ""
    notes: str = ""
    links: list[str] = field(default_factory=list)
    topics: list[dict[str, str]] = field(default_factory=list)
    pmt_url: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Subject":
        return cls(str(data.get("id", "")), str(data.get("name", "")), str(data.get("exam_board", "")), str(data.get("notes", "")), list(data.get("links", [])), list(data.get("topics", [])), str(data.get("pmt_url", "")))
