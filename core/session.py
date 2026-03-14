from core.documents.factory import create_document
from core.cache_manager import (
    build_cached_result,
    build_dpi_cache_path,
    build_fitted_cache_path,
    enforce_cache_limits,
    is_cache_hit,
)
from core.path_policy import build_cache_dir, build_document_path
from core.config import CACHE_ENABLED, DEFAULT_RENDER_MODE, TARGET_HEIGHT, TARGET_WIDTH
from core.render_reporter import report_render_result
from core.logging_config import get_logger
from storage.state_manager import get_saved_page, load_state, save_progress

logger = get_logger(__name__)


class ReaderSession:
    TARGET_WIDTH = TARGET_WIDTH
    TARGET_HEIGHT = TARGET_HEIGHT

    def __init__(self, category, filename, display=None):
        self.category = category
        self.filename = filename
        logger.info("Initializing reader session for %s/%s.", category, filename)
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
        logger.info("Document created for %s/%s using %s.", category, filename, type(self.document).__name__)
        self.total_pages = self.document.get_total_pages()
        logger.info("Resolved total pages for %s/%s: %s", category, filename, self.total_pages)
        self.current_page = max(1, get_saved_page(self.state, self.book_key))

        if self.current_page > self.total_pages:
            self.current_page = self.total_pages
        logger.info(
            "Reader session ready for %s/%s at page %s/%s.",
            category,
            filename,
            self.current_page,
            self.total_pages,
        )
            

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
        print(f"r     = render current page using default mode ({DEFAULT_RENDER_MODE})")
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

        cache_path = build_dpi_cache_path(self.cache_dir, self.current_page, dpi)
        logger.info(
            "Render requested for %s/%s page=%s dpi=%s.",
            self.category,
            self.filename,
            self.current_page,
            dpi,
        )
        memory_before = self._get_memory_kb()

        try:
            if CACHE_ENABLED and is_cache_hit(cache_path):
                logger.info(
                    "Cache hit for %s/%s page=%s dpi=%s at %s.",
                    self.category,
                    self.filename,
                    self.current_page,
                    dpi,
                    cache_path,
                )
                result = build_cached_result(
                    cache_path,
                    mode="DPI render (cache hit)",
                    extra={
                        "dpi": dpi,
                        "cache_hit": True,
                    },
                )
            else:
                logger.info(
                    "Cache miss for %s/%s page=%s dpi=%s. Rendering new image.",
                    self.category,
                    self.filename,
                    self.current_page,
                    dpi,
                )
                result = self.document.render_page_dpi(self.current_page, dpi)
                enforce_cache_limits(self.cache_dir)
                result.setdefault("extra", {})
                result["extra"]["cache_hit"] = False

            memory_after = self._get_memory_kb()
            report_render_result(self.display, result, memory_before, memory_after)
        except ValueError as e:
            logger.warning(
                "Render failed for %s/%s page=%s dpi=%s: %s",
                self.category,
                self.filename,
                self.current_page,
                dpi,
                e,
            )
            print(f"Render failed: {e}")
        except Exception:
            logger.exception(
                "Unexpected render failure for %s/%s page=%s dpi=%s.",
                self.category,
                self.filename,
                self.current_page,
                dpi,
            )
            print("Render failed: unexpected error.")

    def render_current_page_fitted(self):
        if not self.document_path.exists():
            print("Render failed: file does not exist.")
            return

        cache_path = build_fitted_cache_path(
            self.cache_dir,
            self.current_page,
            self.TARGET_WIDTH,
            self.TARGET_HEIGHT,
        )
        logger.info(
            "Fitted render requested for %s/%s page=%s target=%sx%s.",
            self.category,
            self.filename,
            self.current_page,
            self.TARGET_WIDTH,
            self.TARGET_HEIGHT,
        )
        memory_before = self._get_memory_kb()

        try:
            if CACHE_ENABLED and is_cache_hit(cache_path):
                logger.info(
                    "Fitted render cache hit for %s/%s page=%s at %s.",
                    self.category,
                    self.filename,
                    self.current_page,
                    cache_path,
                )
                result = build_cached_result(
                    cache_path,
                    mode="fitted render (cache hit)",
                    extra={
                        "target_width": self.TARGET_WIDTH,
                        "target_height": self.TARGET_HEIGHT,
                        "cache_hit": True,
                    },
                )
            else:
                logger.info(
                    "Fitted render cache miss for %s/%s page=%s. Rendering new image.",
                    self.category,
                    self.filename,
                    self.current_page,
                )
                result = self.document.render_page_fitted(
                    self.current_page,
                    self.TARGET_WIDTH,
                    self.TARGET_HEIGHT,
                )
                enforce_cache_limits(self.cache_dir)
                result.setdefault("extra", {})
                result["extra"]["cache_hit"] = False

            memory_after = self._get_memory_kb()
            report_render_result(self.display, result, memory_before, memory_after)
        except ValueError as e:
            logger.warning(
                "Fitted render failed for %s/%s page=%s: %s",
                self.category,
                self.filename,
                self.current_page,
                e,
            )
            print(f"Render failed: {e}")
        except Exception:
            logger.exception(
                "Unexpected fitted render failure for %s/%s page=%s.",
                self.category,
                self.filename,
                self.current_page,
            )
            print("Render failed: unexpected error.")

    def render_current_page_default(self):
        if DEFAULT_RENDER_MODE == "fit":
            self.render_current_page_fitted()
        elif DEFAULT_RENDER_MODE == "r100":
            self.render_current_page(100)
        elif DEFAULT_RENDER_MODE == "r150":
            self.render_current_page(150)
        elif DEFAULT_RENDER_MODE == "r200":
            self.render_current_page(200)
        else:
            logger.warning(
                "Unknown DEFAULT_RENDER_MODE '%s'. Falling back to fitted render.",
                DEFAULT_RENDER_MODE,
            )
            self.render_current_page_fitted()

    def handle_render_command(self, command):
        if command == "r":
            self.render_current_page_default()
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
        logger.info(
            "Saving progress for %s/%s at page %s/%s.",
            self.category,
            self.filename,
            self.current_page,
            self.total_pages,
        )
        save_progress(
            self.state,
            self.book_key,
            self.category,
            self.filename,
            self.current_page,
        )
        print(f"Saved progress: page {self.current_page}/{self.total_pages}")