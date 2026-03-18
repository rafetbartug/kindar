from library.catalog import list_category_files


def list_category(category):
    return list_category_files(category)


def _format_last_opened(state):
    last_opened = state.get("last_opened")
    if not last_opened:
        return "No recent book"

    filename = last_opened.get("filename", "Unknown")
    page = last_opened.get("page", "?")
    return f"Recent: {filename} (page {page})"


def show_main_menu(state):
    print("\n[KINDAR]")
    print(_format_last_opened(state))
    print()
    print("1  Continue")
    print("2  Manga")
    print("3  Books")
    print("0  Exit")