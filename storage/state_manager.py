import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
STATE_DIR = os.path.join(PROJECT_ROOT, "state")
STATE_FILE = os.path.join(STATE_DIR, "reading_state.json")


def ensure_state_file():
    os.makedirs(STATE_DIR, exist_ok=True)
    if not os.path.exists(STATE_FILE):
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump({"books": {}, "last_opened": None}, f, indent=2)


def load_state():
    ensure_state_file()
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def get_saved_page(state, book_key):
    return state.get("books", {}).get(book_key, {}).get("page", 1)


def save_progress(state, book_key, category, filename, page):
    state.setdefault("books", {})
    state["books"][book_key] = {
        "category": category,
        "filename": filename,
        "page": page
    }
    state["last_opened"] = {
        "category": category,
        "filename": filename,
        "page": page
    }
    save_state(state)