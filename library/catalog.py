import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
LIBRARY_DIR = os.path.join(PROJECT_ROOT, "library")

CATEGORY_EXTENSIONS = {
    "manga": {".cbz"},
    "books": {".pdf"},
}


def natural_sort_key(value):
    parts = re.split(r"(\d+)", value.lower())
    return [int(part) if part.isdigit() else part for part in parts]


def list_category_files(category):
    path = os.path.join(LIBRARY_DIR, category)
    if not os.path.exists(path):
        return []

    allowed_exts = CATEGORY_EXTENSIONS.get(category, set())
    files = []

    for filename in os.listdir(path):
        if filename.startswith('.'):
            continue

        full_path = os.path.join(path, filename)
        _, ext = os.path.splitext(filename.lower())

        if not os.path.isfile(full_path):
            continue

        if ext not in allowed_exts:
            continue

        try:
            if os.path.getsize(full_path) == 0:
                continue
        except OSError:
            continue

        files.append(filename)

    files.sort(key=natural_sort_key)
    return files
