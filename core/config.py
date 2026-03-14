
import os
from pathlib import Path


def _get_int_env(name: str, default: int) -> int:
    raw_value = os.environ.get(name)
    if raw_value is None:
        return default

    try:
        return int(raw_value)
    except (TypeError, ValueError):
        return default


def _get_float_env(name: str, default: float) -> float:
    raw_value = os.environ.get(name)
    if raw_value is None:
        return default

    try:
        return float(raw_value)
    except (TypeError, ValueError):
        return default


BASE_DIR = Path(__file__).resolve().parent.parent
LIBRARY_DIR = BASE_DIR / "library"
CACHE_DIR = BASE_DIR / "cache"
LOG_DIR = BASE_DIR / "logs"
STATE_DIR = BASE_DIR / "state"

DISPLAY_BACKEND = os.environ.get("KINDAR_DISPLAY", "terminal").strip().lower()
LOG_LEVEL = os.environ.get("KINDAR_LOG_LEVEL", "INFO").strip().upper()

TARGET_WIDTH = _get_int_env("KINDAR_TARGET_WIDTH", 800)
TARGET_HEIGHT = _get_int_env("KINDAR_TARGET_HEIGHT", 600)
DEFAULT_RENDER_MODE = os.environ.get("KINDAR_DEFAULT_RENDER_MODE", "fit").strip().lower()

CACHE_ENABLED = os.environ.get("KINDAR_CACHE_ENABLED", "1").strip().lower() not in {"0", "false", "no"}
CACHE_MAX_SIZE_MB = _get_int_env("KINDAR_CACHE_MAX_SIZE_MB", 256)
CACHE_MAX_SIZE_BYTES = CACHE_MAX_SIZE_MB * 1024 * 1024
CACHE_CLEANUP_TARGET_RATIO = _get_float_env("KINDAR_CACHE_CLEANUP_TARGET_RATIO", 0.8)
CACHE_IMAGE_EXTENSION = ".png"