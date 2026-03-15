from datetime import datetime

def log(msg):

    with open("data/logs/agent.log","a") as f:
        f.write(f"{datetime.now()} {msg}\n")
