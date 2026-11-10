from __future__ import annotations

import argparse
import sys

from . import __version__
from .models import PRIORITIES, Task
from .storage import TaskStore

RESET, RED, GREEN, YELLOW, DIM = "\033[0m", "\033[31m", "\033[32m", "\033[33m", "\033[2m"
PRIO_COLOR = {"high": RED, "medium": YELLOW, "low": GREEN}
PRIO_ORDER = {"high": 0, "medium": 1, "low": 2}


def fmt(task: Task) -> str:
    box = "[x]" if task.done else "[ ]"
    prio = f"{PRIO_COLOR[task.priority]}{task.priority:<6}{RESET}"
    due = f" due {task.due}" if task.due else ""
    if task.overdue:
        due = f"{RED}{due} (OVERDUE){RESET}"
    tags = f" {DIM}#{' #'.join(task.tags)}{RESET}" if task.tags else ""
    title = f"{DIM}{task.title}{RESET}" if task.done else task.title
    return f"{task.id:>3} {box} {prio} {title}{due}{tags}"


def show(tasks: list[Task]) -> None:
    if not tasks:
        print("No tasks found.")
        return
    for t in tasks:
        print(fmt(t))


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="taskflow", description="A fast command-line task manager.")
    p.add_argument("--version", action="version", version=f"taskflow {__version__}")
    sub = p.add_subparsers(dest="command", required=True)

    a = sub.add_parser("add", help="add a task")
    a.add_argument("title")
    a.add_argument("-p", "--priority", choices=PRIORITIES, default="medium")
    a.add_argument("-d", "--due", help="due date, YYYY-MM-DD")
    a.add_argument("-t", "--tag", action="append", default=[], help="repeatable")

    l = sub.add_parser("list", help="list tasks")
    l.add_argument("--pending", action="store_true", help="only unfinished tasks")
    l.add_argument("--overdue", action="store_true", help="only overdue tasks")
    l.add_argument("--tag", help="filter by tag")

    for name, text in (("done", "mark task complete"), ("undone", "reopen a task"),
                       ("delete", "delete a task")):
        c = sub.add_parser(name, help=text)
        c.add_argument("id", type=int)

    s = sub.add_parser("search", help="search titles and tags")
    s.add_argument("query")

    sub.add_parser("stats", help="show statistics")
    return p


def run(args: argparse.Namespace, store: TaskStore) -> None:
    cmd = args.command
    if cmd == "add":
        task = store.add(args.title, args.priority, args.due, args.tag)
        print(f"Added task #{task.id}: {task.title}")
    elif cmd == "list":
        tasks = store.tasks
        if args.pending:
            tasks = [t for t in tasks if not t.done]
        if args.overdue:
            tasks = [t for t in tasks if t.overdue]
        if args.tag:
            tasks = [t for t in tasks if args.tag in t.tags]
        show(sorted(tasks, key=lambda t: (t.done, PRIO_ORDER[t.priority], t.due or "9999")))
    elif cmd == "done":
        print(f"Completed: {store.set_done(args.id).title}")
    elif cmd == "undone":
        print(f"Reopened: {store.set_done(args.id, False).title}")
    elif cmd == "delete":
        print(f"Deleted: {store.delete(args.id).title}")
    elif cmd == "search":
        show(store.search(args.query))
    elif cmd == "stats":
        s = store.stats()
        print(f"Total: {s['total']}  Done: {s['done']}  Pending: {s['pending']}  "
              f"Overdue: {s['overdue']}  Completion: {s['completion_rate']}%")


def main(argv=None, store: TaskStore | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        run(args, store or TaskStore())
    except (ValueError, KeyError, RuntimeError) as exc:
        print(f"Error: {exc.args[0] if exc.args else exc}", file=sys.stderr)
        return 1
    return 0
