import os
from storage.state_manager import ensure_state_file, load_state
from ui.menu import list_category, show_main_menu
from core.reader import open_reader

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LIBRARY_DIR = os.path.join(BASE_DIR, "library")


def continue_reading():
    state = load_state()
    last_opened = state.get("last_opened")

    if not last_opened:
        print("No previous reading state found.")
        return

    category = last_opened["category"]
    filename = last_opened["filename"]
    open_reader(category, filename)


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

    while True:
        state = load_state()
        show_main_menu(state)
        choice = input("Choice: ").strip()

        if choice == "1":
            continue_reading()
        elif choice == "2":
            files = list_category("manga")
            selected = select_file(files)
            if selected:
                open_reader("manga", selected)
        elif choice == "3":
            files = list_category("books")
            selected = select_file(files)
            if selected:
                open_reader("books", selected)
        elif choice == "0":
            print("Goodbye.")
            break
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()