from core.logging_config import get_logger, setup_logging
from storage.state_manager import ensure_state_file, load_state
from core.storage.crash_state_manager import (
    ensure_crash_state_file,
    mark_app_start,
    mark_clean_exit,
    record_crash,
)
from ui.menu import list_category, show_main_menu
from core.reader_controller import open_reader
from core.recovery import handle_recovery_flow
from display.terminal_display import TerminalDisplay
from display.eink_display import EinkDisplay
from core.config import DISPLAY_BACKEND, TARGET_HEIGHT, TARGET_WIDTH

logger = get_logger(__name__)


def run_app():
    ensure_state_file()
    ensure_crash_state_file()
    crash_state = mark_app_start()

    if crash_state.recovery_required:
        logger.error(
            "Recovery required after %s consecutive unclean startups.",
            crash_state.consecutive_startup_failures,
        )
        should_continue = handle_recovery_flow(crash_state)
        if not should_continue:
            mark_clean_exit()
            print("Exiting recovery mode.")
            return

    display = build_display()
    logger.info("Display initialized: %s", type(display).__name__)

    while True:
        state = load_state()
        show_main_menu(state)
        choice = input("Choice: ").strip()

        if choice == "1":
            continue_reading(display)
        elif choice == "2":
            files = list_category("manga")
            selected = select_file(files)
            if selected:
                logger.info("Opening manga: %s", selected)
                open_reader("manga", selected, display=display)
        elif choice == "3":
            files = list_category("books")
            selected = select_file(files)
            if selected:
                logger.info("Opening book: %s", selected)
                open_reader("books", selected, display=display)
        elif choice == "0":
            logger.info("Kindar shutting down from main menu.")
            print("Goodbye.")
            mark_clean_exit()
            break
        else:
            print("Invalid choice.")

def build_display():
    backend = DISPLAY_BACKEND

    if backend == "terminal":
        logger.info("Using terminal display backend.")
        return TerminalDisplay(TARGET_WIDTH, TARGET_HEIGHT)

    if backend == "eink":
        logger.info("Using e-ink display backend.")
        return EinkDisplay(TARGET_WIDTH, TARGET_HEIGHT)

    logger.warning("Unknown display backend '%s', falling back to terminal.", backend)
    print(f"Unknown display backend '{backend}', falling back to terminal.")
    return TerminalDisplay(TARGET_WIDTH, TARGET_HEIGHT)


def continue_reading(display):
    state = load_state()
    last_opened = state.get("last_opened")

    if not last_opened:
        logger.info("No previous reading state found for continue reading.")
        print("No previous reading state found.")
        return

    category = last_opened.get("category")
    filename = last_opened.get("filename")

    if category not in {"manga", "books"}:
        logger.warning("Invalid category in saved state during continue reading: %r", category)
        print("Invalid category in saved state.")
        return

    if not filename:
        logger.warning("Invalid filename in saved state during continue reading: %r", filename)
        print("Invalid filename in saved state.")
        return

    from core.config import LIBRARY_DIR
    file_path = LIBRARY_DIR / category / filename

    if not file_path.exists() or not file_path.is_file():
        logger.warning(
            "Saved file missing during continue reading: %s/%s (%s)",
            category,
            filename,
            file_path,
        )
        print("Saved file no longer exists.")
        return

    try:
        logger.info("Resuming reading for %s/%s.", category, filename)
        open_reader(category, filename, display=display)
    except Exception:
        logger.exception("Failed to resume reading for %s/%s.", category, filename)
        print("Failed to resume reading.")
        return


def select_file(files):
    if not files:
        print("No supported files found.")
        return None

    for i, file in enumerate(files, start=1):
        print(f"{i}. {file}")

    choice = input("Select file (0 to cancel): ").strip()

    if not choice.isdigit():
        print("Invalid input.")
        return None

    choice = int(choice)

    if choice == 0:
        return None

    if 1 <= choice <= len(files):
        return files[choice - 1]

    print("Invalid selection.")
    return None


def main():
    setup_logging()
    logger.info("Kindar starting up.")

    try:
        run_app()
    except KeyboardInterrupt:
        logger.info("Kindar interrupted by user.")
        print("Interrupted.")
        mark_clean_exit()
    except Exception as exc:
        logger.exception("Fatal top-level crash during Kindar runtime.")
        record_crash(str(exc), "main_loop")
        print("Fatal error. Kindar will need restart or recovery handling.")
        raise


if __name__ == "__main__":
    main()