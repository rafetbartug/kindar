import json
import os
from core.logging_config import get_logger

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
STATE_DIR = os.path.join(PROJECT_ROOT, "state")
STATE_FILE = os.path.join(STATE_DIR, "reading_state.json")

logger = get_logger(__name__)


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
        logger.info("State file not found. Creating default state at %s", STATE_FILE)
        save_state(_default_state())


def load_state():
    ensure_state_file()

    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            state = json.load(f)
    except json.JSONDecodeError:
        logger.warning("Invalid JSON in state file. Falling back to default state: %s", STATE_FILE)
        state = _default_state()
    except OSError as e:
        logger.warning("Could not read state file %s: %s. Falling back to default state.", STATE_FILE, e)
        state = _default_state()

    if not isinstance(state, dict):
        logger.warning("State root is not a dictionary. Resetting to default state.")
        state = _default_state()

    legacy_books = state.pop("books", None)
    progress = state.get("progress")

    if not isinstance(progress, dict):
        logger.warning("State progress section is invalid. Resetting progress to empty dictionary.")
        progress = {}

    if isinstance(legacy_books, dict):
        logger.info("Migrating legacy 'books' state entries into 'progress'.")
        progress.update(legacy_books)

    normalized_progress = {}
    for book_key, entry in progress.items():
        if not isinstance(book_key, str) or not isinstance(entry, dict):
            logger.warning("Skipping invalid progress entry for key=%r.", book_key)
            continue

        category = entry.get("category")
        filename = entry.get("filename")
        page = _normalize_page(entry.get("page", 1))

        if not isinstance(category, str) or not category.strip():
            logger.warning("Skipping progress entry with invalid category for key=%r.", book_key)
            continue
        if not isinstance(filename, str) or not filename.strip():
            logger.warning("Skipping progress entry with invalid filename for key=%r.", book_key)
            continue

        normalized_progress[book_key] = {
            "category": category,
            "filename": filename,
            "page": page,
        }

    last_opened = state.get("last_opened")
    if last_opened is None:
        normalized_last_opened = None
    elif isinstance(last_opened, dict):
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
            logger.warning("Dropping invalid last_opened entry from state.")
            normalized_last_opened = None
    else:
        logger.warning(
            "State last_opened section is invalid. Dropping value of type %s.",
            type(last_opened).__name__,
        )
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

    logger.debug("Persisting state atomically to %s", STATE_FILE)
    os.replace(temp_file, STATE_FILE)


def get_saved_page(state, book_key):
    page = state.get("progress", {}).get(book_key, {}).get("page", 1)
    return _normalize_page(page)


def save_progress(state, book_key, category, filename, page):
    normalized_page = _normalize_page(page)
    logger.info(
        "Saving progress for %s at page %s (%s/%s).",
        book_key,
        normalized_page,
        category,
        filename,
    )

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
    if "books" in state:
        logger.info("Removing legacy 'books' key during progress save.")
    state.pop("books", None)
    save_state(state)