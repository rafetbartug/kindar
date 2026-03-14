from pathlib import Path

from PIL import Image

from core.config import (
    CACHE_CLEANUP_TARGET_RATIO,
    CACHE_ENABLED,
    CACHE_IMAGE_EXTENSION,
    CACHE_MAX_SIZE_BYTES,
)
from core.logging_config import get_logger

logger = get_logger(__name__)


def build_dpi_cache_path(cache_dir, page_number, dpi):
    return Path(cache_dir) / f"page_{page_number:04d}_{dpi}dpi{CACHE_IMAGE_EXTENSION}"


def build_fitted_cache_path(cache_dir, page_number, target_width, target_height):
    return Path(cache_dir) / (
        f"page_{page_number:04d}_fit_{target_width}x{target_height}{CACHE_IMAGE_EXTENSION}"
    )


def is_cache_hit(cache_path):
    path = Path(cache_path)
    return path.exists() and path.is_file()



def build_cached_result(cache_path, mode, extra=None):
    path = Path(cache_path)

    with Image.open(path) as image:
        width, height = image.size

    return {
        "output_path": path,
        "width": width,
        "height": height,
        "mode": mode,
        "extra": extra or {},
    }


def list_cache_files(cache_dir):
    path = Path(cache_dir)
    if not path.exists() or not path.is_dir():
        return []

    return sorted(
        [
            item
            for item in path.rglob("*")
            if item.is_file() and item.suffix.lower() == CACHE_IMAGE_EXTENSION.lower()
        ]
    )



def count_cache_files(cache_dir):
    return len(list_cache_files(cache_dir))



def get_total_cache_size_bytes(cache_dir):
    total_size = 0

    for cache_file in list_cache_files(cache_dir):
        try:
            total_size += cache_file.stat().st_size
        except OSError:
            logger.warning("Could not read cache file size: %s", cache_file)

    return total_size



def prune_cache_if_needed(cache_dir):
    if not CACHE_ENABLED:
        return 0

    max_size = CACHE_MAX_SIZE_BYTES
    if max_size <= 0:
        return 0

    target_size = int(max_size * CACHE_CLEANUP_TARGET_RATIO)
    if target_size < 0:
        target_size = 0

    cache_files = []
    total_size = 0

    for cache_file in list_cache_files(cache_dir):
        try:
            stat_result = cache_file.stat()
            cache_files.append((cache_file, stat_result.st_mtime, stat_result.st_size))
            total_size += stat_result.st_size
        except OSError:
            logger.warning("Could not stat cache file during cleanup: %s", cache_file)

    if total_size <= max_size:
        return 0

    logger.info(
        "Cache size exceeded limit for %s: total=%s bytes, max=%s bytes. Starting cleanup.",
        cache_dir,
        total_size,
        max_size,
    )

    cache_files.sort(key=lambda item: item[1])

    removed_count = 0
    freed_bytes = 0

    for cache_file, _mtime, file_size in cache_files:
        if total_size <= target_size:
            break

        try:
            cache_file.unlink()
            total_size -= file_size
            freed_bytes += file_size
            removed_count += 1
            logger.info("Deleted old cache file: %s", cache_file)
        except OSError as exc:
            logger.warning("Could not delete cache file %s: %s", cache_file, exc)

    logger.info(
        "Cache cleanup finished for %s. Deleted=%s files, freed=%s bytes, remaining=%s bytes.",
        cache_dir,
        removed_count,
        freed_bytes,
        total_size,
    )

    return removed_count



def enforce_cache_limits(cache_dir):
    return prune_cache_if_needed(cache_dir)


def clear_document_cache(cache_dir):
    removed_count = 0

    for cache_file in list_cache_files(cache_dir):
        try:
            cache_file.unlink()
            removed_count += 1
        except OSError as exc:
            logger.warning("Could not delete cache file %s: %s", cache_file, exc)
            continue

    return removed_count