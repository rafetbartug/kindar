

from core.session import ReaderSession
from core.logging_config import get_logger


logger = get_logger(__name__)


def open_reader(category, filename, display=None):
    try:
        logger.info("Opening reader session for %s/%s.", category, filename)
        session = ReaderSession(category, filename, display=display)
    except ValueError as e:
        logger.warning("Cannot open reader for %s/%s: %s", category, filename, e)
        print(f"Cannot open reader: {e}")
        return
    except Exception:
        logger.exception("Unexpected error while opening reader for %s/%s.", category, filename)
        print("Cannot open reader: unexpected error.")
        return

    session.show_opening_message()
    logger.info("Reader session started for %s/%s.", category, filename)

    while True:
        session.show_status()
        command = input("Command: ").strip().lower()
        logger.debug("Reader command received for %s/%s: %s", category, filename, command)

        if command == "n":
            session.next_page()
        elif command == "p":
            session.prev_page()
        elif command in {"r", "r100", "r150", "r200", "rf"}:
            session.handle_render_command(command)
        elif command == "q":
            logger.info("Saving and closing reader for %s/%s.", category, filename)
            session.save_and_quit()
            break
        else:
            logger.warning("Invalid reader command for %s/%s: %s", category, filename, command)
            print("Invalid command.")