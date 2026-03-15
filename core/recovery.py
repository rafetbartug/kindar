

from __future__ import annotations

from pathlib import Path
import shutil

from core.logging_config import get_logger
from core.storage.crash_state_manager import (
    clear_recovery_required,
    reset_crash_state,
)
from storage.state_manager import load_state, save_state

logger = get_logger(__name__)

CACHE_ROOT = Path("cache")


def clear_last_opened() -> None:
    state = load_state()
    state["last_opened"] = None
    save_state(state)
    logger.info("Recovery action: cleared last_opened state.")


def clear_cache(cache_root: Path | str = CACHE_ROOT) -> None:
    cache_path = Path(cache_root)

    if not cache_path.exists():
        logger.info("Recovery action: cache directory does not exist, nothing to clear.")
        return

    for child in cache_path.iterdir():
        if child.is_dir():
            shutil.rmtree(child, ignore_errors=True)
        else:
            try:
                child.unlink()
            except FileNotFoundError:
                pass

    logger.info("Recovery action: cache cleared from %s.", cache_path)


def show_recovery_menu(crash_state) -> str:
    print("\n=== KINDAR RECOVERY ===")
    print(
        f"Consecutive unclean startups: {crash_state.consecutive_startup_failures}"
    )

    if crash_state.last_crash_phase:
        print(f"Last crash phase : {crash_state.last_crash_phase}")
    if crash_state.last_crash_reason:
        print(f"Last crash reason: {crash_state.last_crash_reason}")
    if crash_state.last_crash_time:
        print(f"Last crash time  : {crash_state.last_crash_time}")

    print("1. Retry normal startup")
    print("2. Clear continue-reading state and open normally")
    print("3. Reset crash state")
    print("4. Clear cache")
    print("0. Exit")
    return input("Recovery choice: ").strip()


def handle_recovery_flow(crash_state) -> bool:
    while True:
        choice = show_recovery_menu(crash_state)

        if choice == "1":
            clear_recovery_required()
            logger.info("Recovery action: retry normal startup selected.")
            return True

        if choice == "2":
            clear_last_opened()
            clear_recovery_required()
            logger.info(
                "Recovery action: cleared continue-reading state and retrying startup."
            )
            return True

        if choice == "3":
            reset_crash_state()
            logger.info("Recovery action: crash state reset selected.")
            return True

        if choice == "4":
            clear_cache()
            print("Cache cleared.")
            continue

        if choice == "0":
            logger.info("Recovery action: exit selected.")
            return False

        print("Invalid recovery choice.")