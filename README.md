# TaskFlow

A fast, dependency-free command-line task manager written in Python.

## Features
- Priorities (low / medium / high) and due dates with overdue detection
- Tags, search, and filters
- Statistics and completion rate
- Safe atomic JSON storage (no data loss on crash)
- Unit tests and GitHub Actions CI

## Install
```bash
pip install -e .
```

## Usage
```bash
taskflow add "Finish report" -p high -d 2026-12-01 -t work
taskflow add "Buy milk" -t home
taskflow list
taskflow list --pending --tag work
taskflow done 1
taskflow search milk
taskflow stats
```
You can also run it without installing: `python -m taskflow list`.

Tasks are saved in `~/.taskflow.json`. Set the `TASKFLOW_FILE` environment variable to change the location.

## Tests
```bash
pip install pytest
pytest
```

## License
MIT
