from datetime import date, timedelta

import pytest

from taskflow.cli import main
from taskflow.models import Task
from taskflow.storage import TaskStore


@pytest.fixture
def store(tmp_path):
    return TaskStore(tmp_path / "tasks.json")


def test_add_and_persist(store, tmp_path):
    store.add("Write code", "high", tags=["dev"])
    reloaded = TaskStore(tmp_path / "tasks.json")
    assert len(reloaded.tasks) == 1
    assert reloaded.tasks[0].priority == "high"


def test_ids_increment_after_delete(store):
    a = store.add("a")
    store.add("b")
    store.delete(a.id)
    assert store.add("c").id == 3


def test_validation():
    with pytest.raises(ValueError):
        Task(1, "  ")
    with pytest.raises(ValueError):
        Task(1, "x", priority="urgent")
    with pytest.raises(ValueError):
        Task(1, "x", due="31-12-2026")


def test_done_and_stats(store):
    t = store.add("one")
    store.add("two")
    store.set_done(t.id)
    s = store.stats()
    assert s["done"] == 1 and s["pending"] == 1 and s["completion_rate"] == 50.0


def test_overdue(store):
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    t = store.add("late", due=yesterday)
    assert t.overdue
    store.set_done(t.id)
    assert not t.overdue


def test_search(store):
    store.add("Buy milk", tags=["home"])
    store.add("Deploy app", tags=["work"])
    assert [t.title for t in store.search("milk")] == ["Buy milk"]
    assert [t.title for t in store.search("work")] == ["Deploy app"]


def test_missing_task(store):
    with pytest.raises(KeyError):
        store.get(99)


def test_cli_flow(store, capsys):
    assert main(["add", "Ship it", "-p", "high"], store) == 0
    assert main(["done", "1"], store) == 0
    assert main(["done", "42"], store) == 1
    main(["stats"], store)
    assert "Completion: 100.0%" in capsys.readouterr().out
