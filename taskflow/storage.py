from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

from .models import Task


def default_path() -> Path:
    return Path(os.environ.get("TASKFLOW_FILE", Path.home() / ".taskflow.json"))


class TaskStore:
    """JSON-backed task storage with atomic writes."""

    def __init__(self, path: Path | None = None):
        self.path = Path(path) if path else default_path()
        self.tasks: list[Task] = []
        self._load()

    def _load(self) -> None:
        if not self.path.exists():
            return
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"Corrupted data file {self.path}: {exc}") from exc
        self.tasks = [Task.from_dict(item) for item in raw]

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=self.path.parent, suffix=".tmp")
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump([t.to_dict() for t in self.tasks], fh, indent=2)
        os.replace(tmp, self.path)  # atomic: never leaves a half-written file

    def _next_id(self) -> int:
        return max((t.id for t in self.tasks), default=0) + 1

    def add(self, title, priority="medium", due=None, tags=None) -> Task:
        task = Task(self._next_id(), title.strip(), priority, due, tags or [])
        self.tasks.append(task)
        self.save()
        return task

    def get(self, task_id: int) -> Task:
        for t in self.tasks:
            if t.id == task_id:
                return t
        raise KeyError(f"No task with id {task_id}.")

    def set_done(self, task_id: int, done: bool = True) -> Task:
        task = self.get(task_id)
        task.done = done
        self.save()
        return task

    def delete(self, task_id: int) -> Task:
        task = self.get(task_id)
        self.tasks.remove(task)
        self.save()
        return task

    def search(self, query: str) -> list[Task]:
        q = query.lower()
        return [t for t in self.tasks
                if q in t.title.lower() or any(q in tag.lower() for tag in t.tags)]

    def stats(self) -> dict:
        total = len(self.tasks)
        done = sum(t.done for t in self.tasks)
        return {
            "total": total,
            "done": done,
            "pending": total - done,
            "overdue": sum(t.overdue for t in self.tasks),
            "completion_rate": round(done / total * 100, 1) if total else 0.0,
        }
