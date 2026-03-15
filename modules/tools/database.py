import json
from pathlib import Path

DB="data/wisdom_db.json"

def save(entry):

    Path("data").mkdir(exist_ok=True)

    with open(DB,"a") as f:
        json.dump(entry,f)
        f.write("\n")
