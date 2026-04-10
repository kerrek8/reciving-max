import json
import os

FILE = "threads.json"


def load_threads():
    if not os.path.exists(FILE):
        return {}

    with open(FILE, "r") as f:
        return json.load(f)


def save_threads(data):
    with open(FILE, "w") as f:
        json.dump(data, f)


threads = load_threads()