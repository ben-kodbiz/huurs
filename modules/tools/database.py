import json
from pathlib import Path
from datetime import datetime

DB="data/wisdom_db.json"

def save(entry):
    """
    Save a wisdom entry to the database.
    
    Args:
        entry: Dict containing source, text, quran_reference, and optionally topics
    """
    Path("data").mkdir(exist_ok=True)

    # Add metadata
    entry["created_at"] = datetime.now().isoformat()
    entry["id"] = generate_id(entry)

    with open(DB, "a") as f:
        json.dump(entry, f)
        f.write("\n")

def generate_id(entry):
    """Generate a unique ID for the entry based on source and timestamp."""
    import hashlib
    source = entry.get("source", "")
    timestamp = datetime.now().isoformat()
    return hashlib.md5(f"{source}{timestamp}".encode()).hexdigest()[:12]

def load_all():
    """Load all entries from the database."""
    if not Path(DB).exists():
        return []
    
    entries = []
    with open(DB, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                entries.append(json.loads(line))
    return entries
