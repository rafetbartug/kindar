

from core.session import ReaderSession


def open_reader(category, filename, display=None):
    try:
        session = ReaderSession(category, filename, display=display)
    except ValueError as e:
        print(f"Cannot open reader: {e}")
        return
    except Exception:
        print("Cannot open reader: unexpected error.")
        return

    session.show_opening_message()

    while True:
        session.show_status()
        command = input("Command: ").strip().lower()

        if command == "n":
            session.next_page()
        elif command == "p":
            session.prev_page()
        elif command in {"r", "r100", "r150", "r200", "rf"}:
            session.handle_render_command(command)
        elif command == "q":
            session.save_and_quit()
            break
        else:
            print("Invalid command.")