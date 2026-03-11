from pathlib import Path

import pymupdf as fitz

from storage.state_manager import load_state, save_progress, get_saved_page


class ReaderSession:
    TARGET_WIDTH = 800
    TARGET_HEIGHT = 600

    def __init__(self, category, filename):
        self.category = category
        self.filename = filename
        self.document_path = self._build_document_path()
        self.cache_dir = self._build_cache_dir()
        self.book_key = f"{category}/{filename}"
        self.state = load_state()
        self.current_page = max(1, get_saved_page(self.state, self.book_key))
        self.total_pages = self._get_total_pages()

        if self.total_pages < 1:
            self.total_pages = 1

        if self.current_page > self.total_pages:
            self.current_page = self.total_pages

    def _build_document_path(self):
        base_dir = Path(__file__).resolve().parent.parent
        return base_dir / "library" / self.category / self.filename

    def _build_cache_dir(self):
        base_dir = Path(__file__).resolve().parent.parent
        cache_dir = base_dir / "cache" / self.category / self.filename.replace(".", "_")
        cache_dir.mkdir(parents=True, exist_ok=True)
        return cache_dir

    def _get_total_pages(self):
        if not self.document_path.exists():
            print(f"File not found: {self.document_path}")
            return 1

        if self.document_path.suffix.lower() != ".pdf":
            print("Currently only PDF files are supported.")
            return 1

        try:
            with fitz.open(self.document_path) as doc:
                return doc.page_count
        except Exception as e:
            print(f"Error opening PDF: {e}")
            return 1

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

        if self.document_path.suffix.lower() != ".pdf":
            print("Render failed: only PDF files are supported.")
            return

        memory_before = self._get_memory_kb()

        try:
            with fitz.open(self.document_path) as doc:
                page = doc.load_page(self.current_page - 1)
                pix = page.get_pixmap(
                    dpi=dpi,
                    colorspace=fitz.csGRAY,
                    alpha=False,
                )

                output_path = self.cache_dir / f"page_{self.current_page:04d}_{dpi}dpi.png"
                pix.save(output_path)

                memory_after = self._get_memory_kb()

                print("\nRender complete.")
                print("Mode       : DPI render")
                print(f"Saved to   : {output_path}")
                print(f"Image size : {pix.width}x{pix.height}")
                print(f"Memory before: {memory_before} kB")
                print(f"Memory after : {memory_after} kB")
                if memory_before >= 0 and memory_after >= 0:
                    print(f"Delta        : {memory_after - memory_before} kB")

        except Exception as e:
            print(f"Render error: {e}")

    def render_current_page_fitted(self):
        if not self.document_path.exists():
            print("Render failed: file does not exist.")
            return

        if self.document_path.suffix.lower() != ".pdf":
            print("Render failed: only PDF files are supported.")
            return

        memory_before = self._get_memory_kb()

        try:
            with fitz.open(self.document_path) as doc:
                page = doc.load_page(self.current_page - 1)
                page_rect = page.rect

                scale_x = self.TARGET_WIDTH / page_rect.width
                scale_y = self.TARGET_HEIGHT / page_rect.height
                scale = min(scale_x, scale_y)

                matrix = fitz.Matrix(scale, scale)

                pix = page.get_pixmap(
                    matrix=matrix,
                    colorspace=fitz.csGRAY,
                    alpha=False,
                )

                output_path = self.cache_dir / (
                    f"page_{self.current_page:04d}_fit_"
                    f"{self.TARGET_WIDTH}x{self.TARGET_HEIGHT}.png"
                )
                pix.save(output_path)

                memory_after = self._get_memory_kb()

                print("\nRender complete.")
                print("Mode       : fitted render")
                print(f"Saved to   : {output_path}")
                print(f"Target box : {self.TARGET_WIDTH}x{self.TARGET_HEIGHT}")
                print(f"Image size : {pix.width}x{pix.height}")
                print(f"Scale      : {scale:.3f}")
                print(f"Memory before: {memory_before} kB")
                print(f"Memory after : {memory_after} kB")
                if memory_before >= 0 and memory_after >= 0:
                    print(f"Delta        : {memory_after - memory_before} kB")

        except Exception as e:
            print(f"Render error: {e}")

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


def open_reader(category, filename):
    session = ReaderSession(category, filename)
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