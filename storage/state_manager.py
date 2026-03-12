import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
STATE_DIR = os.path.join(PROJECT_ROOT, "state")
STATE_FILE = os.path.join(STATE_DIR, "reading_state.json")


def _default_state():
    return {"progress": {}, "last_opened": None}


def _normalize_page(page):
    try:
        page = int(page)
    except (TypeError, ValueError):
        return 1

    return max(1, page)


def ensure_state_file():
    os.makedirs(STATE_DIR, exist_ok=True)
    if not os.path.exists(STATE_FILE):
        save_state(_default_state())


def load_state():
    ensure_state_file()

    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            state = json.load(f)
    except (json.JSONDecodeError, OSError):
        state = _default_state()

    if not isinstance(state, dict):
        state = _default_state()

    legacy_books = state.pop("books", None)
    progress = state.get("progress")

    if not isinstance(progress, dict):
        progress = {}

    if isinstance(legacy_books, dict):
        progress.update(legacy_books)

    normalized_progress = {}
    for book_key, entry in progress.items():
        if not isinstance(book_key, str) or not isinstance(entry, dict):
            continue

        category = entry.get("category")
        filename = entry.get("filename")
        page = _normalize_page(entry.get("page", 1))

        if not isinstance(category, str) or not category.strip():
            continue
        if not isinstance(filename, str) or not filename.strip():
            continue

        normalized_progress[book_key] = {
            "category": category,
            "filename": filename,
            "page": page,
        }

    last_opened = state.get("last_opened")
    if isinstance(last_opened, dict):
        category = last_opened.get("category")
        filename = last_opened.get("filename")
        page = _normalize_page(last_opened.get("page", 1))

        if (
            isinstance(category, str) and category.strip()
            and isinstance(filename, str) and filename.strip()
        ):
            normalized_last_opened = {
                "category": category,
                "filename": filename,
                "page": page,
            }
        else:
            normalized_last_opened = None
    else:
        normalized_last_opened = None

    state = {
        "progress": normalized_progress,
        "last_opened": normalized_last_opened,
    }

    return state


def save_state(state):
    os.makedirs(STATE_DIR, exist_ok=True)
    temp_file = f"{STATE_FILE}.tmp"

    with open(temp_file, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)
        f.flush()
        os.fsync(f.fileno())

    os.replace(temp_file, STATE_FILE)


def get_saved_page(state, book_key):
    page = state.get("progress", {}).get(book_key, {}).get("page", 1)
    return _normalize_page(page)


def save_progress(state, book_key, category, filename, page):
    normalized_page = _normalize_page(page)

    state.setdefault("progress", {})
    state["progress"][book_key] = {
        "category": category,
        "filename": filename,
        "page": normalized_page,
    }
    state["last_opened"] = {
        "category": category,
        "filename": filename,
        "page": normalized_page,
    }
    state.pop("books", None)
    save_state(state)