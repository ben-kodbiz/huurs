import json
from pathlib import Path

FILE = "data/checkpoints.json"

def load():
    """Load all checkpoints from file."""
    if not Path(FILE).exists():
        return {}
    return json.loads(Path(FILE).read_text())

def save(task):
    """Mark a task as completed."""
    data = load()
    data[task] = "DONE"
    Path(FILE).write_text(
        json.dumps(data, indent=2)
    )

def is_completed(task):
    """Check if a task is completed."""
    data = load()
    return data.get(task) == "DONE"

def get_completed():
    """Get list of all completed tasks."""
    data = load()
    return [task for task, status in data.items() if status == "DONE"]

def get_pending(tasks):
    """Get list of pending tasks from a given task list."""
    data = load()
    return [task for task in tasks if data.get(task) != "DONE"]

def reset():
    """Reset all checkpoints."""
    Path(FILE).write_text("{}")
