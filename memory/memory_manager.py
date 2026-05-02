import json
import os

MEMORY_FILE = "memory/jarvis_memory.json"


def load_memory():

    if not os.path.exists(MEMORY_FILE):
        return {}

    with open(MEMORY_FILE, "r") as f:
        return json.load(f)


def save_memory(memory):

    os.makedirs(os.path.dirname(MEMORY_FILE), exist_ok=True)
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=4)


def remember(key, value):

    memory = load_memory()

    memory[key] = value.title()

    save_memory(memory)


def recall(key):

    memory = load_memory()

    return memory.get(key, None)