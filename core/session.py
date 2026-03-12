from core.documents.factory import create_document
from core.path_policy import build_cache_dir, build_document_path
from core.render_reporter import report_render_result
from storage.state_manager import get_saved_page, load_state, save_progress


class ReaderSession:
    TARGET_WIDTH = 800
    TARGET_HEIGHT = 600

    def __init__(self, category, filename, display=None):
        self.category = category
        self.filename = filename
        self.document_path = build_document_path(self.category, self.filename)

        if not self.document_path.exists() or not self.document_path.is_file():
            raise ValueError(f"File does not exist: {self.document_path}")

        if display is None:
            raise ValueError("Display is required.")
        self.display = display
        self.cache_dir = build_cache_dir(self.category, self.filename)
        self.book_key = f"{category}/{filename}"
        self.state = load_state()
        self.document = create_document(self.document_path, self.cache_dir)
        self.total_pages = self.document.get_total_pages()
        self.current_page = max(1, get_saved_page(self.state, self.book_key))

        if self.current_page > self.total_pages:
            self.current_page = self.total_pages
            

    def _get_memory_kb(self):
        try:
            with open("/proc/self/status", "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("VmRSS:"):
                        parts = line.split()
                        return int(parts[1])
        except Exception:
            pass
        return -1

    def show_opening_message(self):
        if self.current_page > 1:
            print(
                f"\nResuming '{self.filename}' from page "
                f"{self.current_page}/{self.total_pages}"
            )
        else:
            print(f"\nOpening '{self.filename}' from page 1/{self.total_pages}")

    def show_status(self):
        print(f"\n--- READING: {self.filename} ---")
        print(f"Document path: {self.document_path}")
        print(f"Current page: {self.current_page}/{self.total_pages}")
        print(f"Target screen: {self.TARGET_WIDTH}x{self.TARGET_HEIGHT}")
        print("n     = next page")
        print("p     = previous page")
        print("r     = render current page fitted for e-ink target")
        print("r100  = render at 100 DPI")
        print("r150  = render at 150 DPI")
        print("r200  = render at 200 DPI")
        print("rf    = render page fitted for e-ink target")
        print("q     = save and quit")

    def next_page(self):
        if self.current_page < self.total_pages:
            self.current_page += 1
        else:
            print("Already at the last page.")

    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
        else:
            print("Already at page 1.")

    def render_current_page(self, dpi=100):
        if not self.document_path.exists():
            print("Render failed: file does not exist.")
            return

        memory_before = self._get_memory_kb()

        try:
            result = self.document.render_page_dpi(self.current_page, dpi)
            memory_after = self._get_memory_kb()
            report_render_result(self.display, result, memory_before, memory_after)
        except ValueError as e:
            print(f"Render failed: {e}")
        except Exception:
            print("Render failed: unexpected error.")

    def render_current_page_fitted(self):
        if not self.document_path.exists():
            print("Render failed: file does not exist.")
            return

        memory_before = self._get_memory_kb()

        try:
            result = self.document.render_page_fitted(
                self.current_page,
                self.TARGET_WIDTH,
                self.TARGET_HEIGHT,
            )
            memory_after = self._get_memory_kb()
            report_render_result(self.display, result, memory_before, memory_after)
        except ValueError as e:
            print(f"Render failed: {e}")
        except Exception:
            print("Render failed: unexpected error.")

    def handle_render_command(self, command):
        if command == "r":
            self.render_current_page_fitted()
        elif command == "r100":
            self.render_current_page(100)
        elif command == "r150":
            self.render_current_page(150)
        elif command == "r200":
            self.render_current_page(200)
        elif command == "rf":
            self.render_current_page_fitted()
        else:
            print("Invalid render command.")

    def save_and_quit(self):
        save_progress(
            self.state,
            self.book_key,
            self.category,
            self.filename,
            self.current_page,
        )
        print(f"Saved progress: page {self.current_page}/{self.total_pages}")