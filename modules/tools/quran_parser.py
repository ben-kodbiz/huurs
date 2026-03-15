import re

def detect(text):

    pattern = r"(\d+:\d+)"

    m = re.search(pattern,text)

    if m:
        return m.group(1)
