
from pathlib import Path
import re

BASE_DIR = Path(__file__).resolve().parent.parent
LIBRARY_DIR = BASE_DIR / "library"
CACHE_DIR = BASE_DIR / "cache"


def sanitize_cache_name(filename):
    name = filename.strip().lower()
    name = name.replace(" ", "_")
    name = name.replace(".", "_")
    name = re.sub(r"[^a-z0-9_\-]", "_", name)
    name = re.sub(r"_+", "_", name).strip("_")

    if not name:
        return "unnamed_document"

    return name


def build_document_path(category, filename):
    return LIBRARY_DIR / category / filename


def build_cache_dir(category, filename):
    cache_dir = CACHE_DIR / category / sanitize_cache_name(filename)
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir
