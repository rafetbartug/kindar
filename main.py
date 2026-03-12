import os
from storage.state_manager import ensure_state_file, load_state
from ui.menu import list_category, show_main_menu
from core.reader_controller import open_reader
from display.terminal_display import TerminalDisplay
from display.eink_display import EinkDisplay

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LIBRARY_DIR = os.path.join(BASE_DIR, "library")


def build_display():
    backend = os.environ.get("KINDAR_DISPLAY", "terminal").strip().lower()

    if backend == "terminal":
        return TerminalDisplay(800, 600)

    if backend == "eink":
        return EinkDisplay(800, 600)

    print(f"Unknown display backend '{backend}', falling back to terminal.")
    return TerminalDisplay(800, 600)


def continue_reading(display):
    state = load_state()
    last_opened = state.get("last_opened")

    if not last_opened:
        print("No previous reading state found.")
        return

    category = last_opened.get("category")
    filename = last_opened.get("filename")

    if category not in {"manga", "books"}:
        print("Invalid category in saved state.")
        return

    if not filename:
        print("Invalid filename in saved state.")
        return

    file_path = os.path.join(LIBRARY_DIR, category, filename)

    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        print("Saved file no longer exists.")
        return

    try:
        open_reader(category, filename, display=display)
    except Exception:
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
    ensure_state_file()
    display = build_display()

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
                open_reader("manga", selected, display=display)
        elif choice == "3":
            files = list_category("books")
            selected = select_file(files)
            if selected:
                open_reader("books", selected, display=display)
        elif choice == "0":
            print("Goodbye.")
            break
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()