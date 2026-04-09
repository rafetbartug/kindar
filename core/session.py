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
from core.memory_profiler import (
    append_render_metrics_csv,
    build_render_metrics,
    get_rss_kb,
    now_perf_ms,
)
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

        logger.info(
            "Document created for %s/%s using %s.",
            category,
            filename,
            type(self.document).__name__,
        )

        self.total_pages = self.document.get_total_pages()
        logger.info(
            "Resolved total pages for %s/%s: %s",
            category,
            filename,
            self.total_pages,
        )

        self.current_page = max(1, get_saved_page(self.state, self.book_key))
        if self.current_page > self.total_pages:
            self.current_page = self.total_pages

        self.selected_render_mode = "r150" if self.category == "manga" else "r100"

        logger.info(
            "Reader session ready for %s/%s at page %s/%s.",
            category,
            filename,
            self.current_page,
            self.total_pages,
        )

    def get_selected_render_command(self):
        valid_modes = {"rf", "r100", "r150", "r200"}
        if self.selected_render_mode in valid_modes:
            return self.selected_render_mode
        return "r150" if self.category == "manga" else "r100"

    def cycle_render_mode(self):
        if self.category == "manga":
            modes = ["r150", "r200", "rf", "r100"]
        else:
            modes = ["r100", "r150", "r200", "rf"]

        current = self.get_selected_render_command()
        try:
            index = modes.index(current)
        except ValueError:
            index = 0

        self.selected_render_mode = modes[(index + 1) % len(modes)]
        return self.selected_render_mode

    def sleep_display(self):
        try:
            if getattr(self, "display", None) is not None:
                self.display.clear()
        except Exception as exc:
            print(f"[WARN] Failed to clear/sleep display: {exc}")

    def render_selected_mode(self):
        command = self.get_selected_render_command()

        if command == "rf":
            self.render_current_page_fitted()
        elif command == "r100":
            self.render_current_page(100)
        elif command == "r150":
            self.render_current_page(150)
        elif command == "r200":
            self.render_current_page(200)
        else:
            self.render_current_page_default()

    def show_opening_message(self):
        if self.current_page > 1:
            print(f"\nResume: {self.filename} ({self.current_page}/{self.total_pages})")
        else:
            print(f"\nOpen: {self.filename} (1/{self.total_pages})")

    def show_status(self):
        print("\n[READING]")
        print(self.filename)
        print(f"Page: {self.current_page}/{self.total_pages}")
        print(f"Screen: {self.TARGET_WIDTH}x{self.TARGET_HEIGHT}")
        print()
        print(
            f"Commands: n=next(auto {self.get_selected_render_command()}), "
            f"p=prev(auto {self.get_selected_render_command()}), "
            f"m=change render, r/rf/r100/r150/r200=manual render, q=save and quit"
        )

    def _document_type_name(self):
        return type(self.document).__name__

    def next_page(self, auto_render=False):
        if self.current_page < self.total_pages:
            self.current_page += 1
            if auto_render:
                self.render_selected_mode()
        else:
            print("Already at last page.")

    def prev_page(self, auto_render=False):
        if self.current_page > 1:
            self.current_page -= 1
            if auto_render:
                self.render_selected_mode()
        else:
            print("Already at first page.")

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
        memory_before = get_rss_kb()
        start_ms = now_perf_ms()

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

            memory_after = get_rss_kb()
            elapsed_ms = now_perf_ms() - start_ms
            report_render_result(self.display, result, memory_before, memory_after)

            metrics = build_render_metrics(
                document_type=self._document_type_name(),
                render_mode=f"dpi_{dpi}",
                page=self.current_page,
                target_width=self.TARGET_WIDTH,
                target_height=self.TARGET_HEIGHT,
                cache_hit=result.get("extra", {}).get("cache_hit", False),
                memory_before_kb=memory_before,
                memory_after_kb=memory_after,
                elapsed_ms=elapsed_ms,
                status="ok",
            )
            append_render_metrics_csv(metrics)

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
            memory_after = get_rss_kb()
            elapsed_ms = now_perf_ms() - start_ms
            metrics = build_render_metrics(
                document_type=self._document_type_name(),
                render_mode=f"dpi_{dpi}",
                page=self.current_page,
                target_width=self.TARGET_WIDTH,
                target_height=self.TARGET_HEIGHT,
                cache_hit=False,
                memory_before_kb=memory_before,
                memory_after_kb=memory_after,
                elapsed_ms=elapsed_ms,
                status="error",
                error=str(e),
            )
            append_render_metrics_csv(metrics)

        except Exception:
            logger.exception(
                "Unexpected render failure for %s/%s page=%s dpi=%s.",
                self.category,
                self.filename,
                self.current_page,
                dpi,
            )
            print("Render failed: unexpected error.")
            memory_after = get_rss_kb()
            elapsed_ms = now_perf_ms() - start_ms
            metrics = build_render_metrics(
                document_type=self._document_type_name(),
                render_mode=f"dpi_{dpi}",
                page=self.current_page,
                target_width=self.TARGET_WIDTH,
                target_height=self.TARGET_HEIGHT,
                cache_hit=False,
                memory_before_kb=memory_before,
                memory_after_kb=memory_after,
                elapsed_ms=elapsed_ms,
                status="error",
                error="unexpected error",
            )
            append_render_metrics_csv(metrics)

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
        memory_before = get_rss_kb()
        start_ms = now_perf_ms()

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

            memory_after = get_rss_kb()
            elapsed_ms = now_perf_ms() - start_ms
            report_render_result(self.display, result, memory_before, memory_after)

            metrics = build_render_metrics(
                document_type=self._document_type_name(),
                render_mode="fit",
                page=self.current_page,
                target_width=self.TARGET_WIDTH,
                target_height=self.TARGET_HEIGHT,
                cache_hit=result.get("extra", {}).get("cache_hit", False),
                memory_before_kb=memory_before,
                memory_after_kb=memory_after,
                elapsed_ms=elapsed_ms,
                status="ok",
            )
            append_render_metrics_csv(metrics)

        except ValueError as e:
            logger.warning(
                "Fitted render failed for %s/%s page=%s: %s",
                self.category,
                self.filename,
                self.current_page,
                e,
            )
            print(f"Render failed: {e}")
            memory_after = get_rss_kb()
            elapsed_ms = now_perf_ms() - start_ms
            metrics = build_render_metrics(
                document_type=self._document_type_name(),
                render_mode="fit",
                page=self.current_page,
                target_width=self.TARGET_WIDTH,
                target_height=self.TARGET_HEIGHT,
                cache_hit=False,
                memory_before_kb=memory_before,
                memory_after_kb=memory_after,
                elapsed_ms=elapsed_ms,
                status="error",
                error=str(e),
            )
            append_render_metrics_csv(metrics)

        except Exception:
            logger.exception(
                "Unexpected fitted render failure for %s/%s page=%s.",
                self.category,
                self.filename,
                self.current_page,
            )
            print("Render failed: unexpected error.")
            memory_after = get_rss_kb()
            elapsed_ms = now_perf_ms() - start_ms
            metrics = build_render_metrics(
                document_type=self._document_type_name(),
                render_mode="fit",
                page=self.current_page,
                target_width=self.TARGET_WIDTH,
                target_height=self.TARGET_HEIGHT,
                cache_hit=False,
                memory_before_kb=memory_before,
                memory_after_kb=memory_after,
                elapsed_ms=elapsed_ms,
                status="error",
                error="unexpected error",
            )
            append_render_metrics_csv(metrics)

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
            self.selected_render_mode = "rf"
            self.render_current_page_fitted()
        elif command == "r100":
            self.selected_render_mode = "r100"
            self.render_current_page(100)
        elif command == "r150":
            self.selected_render_mode = "r150"
            self.render_current_page(150)
        elif command == "r200":
            self.selected_render_mode = "r200"
            self.render_current_page(200)
        elif command == "rf":
            self.selected_render_mode = "rf"
            self.render_current_page_fitted()
        elif command == "m":
            new_mode = self.cycle_render_mode()
            print(f"Selected render mode: {new_mode}")
        else:
            print("Invalid command.")

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
        self.sleep_display()
        print(f"Saved: {self.current_page}/{self.total_pages}")