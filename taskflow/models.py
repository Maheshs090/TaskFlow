from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import date, datetime
from typing import Optional

PRIORITIES = ("low", "medium", "high")


@dataclass
class Task:
    id: int
    title: str
    priority: str = "medium"
    due: Optional[str] = None  # ISO date: YYYY-MM-DD
    tags: list = field(default_factory=list)
    done: bool = False
    created: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))

    def __post_init__(self):
        if not self.title.strip():
            raise ValueError("Title cannot be empty.")
        if self.priority not in PRIORITIES:
            raise ValueError(f"Priority must be one of {PRIORITIES}.")
        if self.due:
            date.fromisoformat(self.due)  # raises ValueError if invalid

    @property
    def overdue(self) -> bool:
        return bool(self.due) and not self.done and date.fromisoformat(self.due) < date.today()

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        return cls(**data)
