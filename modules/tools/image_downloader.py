import requests
from pathlib import Path

def download(url,path):

    r = requests.get(url)

    Path(path).parent.mkdir(parents=True,exist_ok=True)

    with open(path,"wb") as f:
        f.write(r.content)

    return path
