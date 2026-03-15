import json
from pathlib import Path

FILE = "data/checkpoints.json"

def load():
    if not Path(FILE).exists():
        return {}
    return json.loads(Path(FILE).read_text())

def save(task):

    data = load()
    data[task] = "DONE"

    Path(FILE).write_text(
        json.dumps(data, indent=2)
    )
