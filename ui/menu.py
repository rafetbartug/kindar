from library.catalog import list_category_files


def list_category(category):
    return list_category_files(category)


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