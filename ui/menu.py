import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
LIBRARY_DIR = os.path.join(PROJECT_ROOT, "library")
ALLOWED_EXTENSIONS = {".pdf", ".cbz"}


def list_category(category):
    path = os.path.join(LIBRARY_DIR, category)
    if not os.path.exists(path):
        return []

    files = []
    for filename in os.listdir(path):
        full_path = os.path.join(path, filename)
        _, ext = os.path.splitext(filename.lower())

        if not os.path.isfile(full_path):
            continue

        if ext not in ALLOWED_EXTENSIONS:
            continue

        # Skip empty or corrupted files (0 byte)
        try:
            if os.path.getsize(full_path) == 0:
                continue
        except OSError:
            continue

        files.append(filename)

    files.sort()
    return files


def show_main_menu(state):
    print("\n=== KINDAR READER ===")

    last_opened = state.get("last_opened")
    if last_opened:
        print(f"Last opened: {last_opened['filename']} (page {last_opened['page']})")
    else:
        print("Last opened: None")

    print("1. Continue Reading")
    print("2. Manga")
    print("3. Books")
    print("0. Exit")