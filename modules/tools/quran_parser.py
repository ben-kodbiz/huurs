import re

def detect(text):
    """
    Detect Quran reference in text.
    
    Returns verse reference like "20:25-26" or None if not found.
    """
    if not text:
        return None
    
    # Pattern 1: Look for chapter:verse format (e.g., 2:153)
    pattern = r"(\d+):(\d+)"
    m = re.search(pattern, text)
    if m:
        return f"{m.group(1)}:{m.group(2)}"
    
    # Pattern 2: Look for standalone Arabic verse numbers
    # Match Arabic-Indic digits (۰-۹)
    arabic_digits = r"[۰-۹]+"
    m = re.findall(arabic_digits, text)
    if m:
        return ":".join(m[:2])  # Return first two numbers as chapter:verse
    
    return None
