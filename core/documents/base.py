

from pathlib import Path


class BaseDocument:
    def __init__(self, document_path, cache_dir):
        self.document_path = Path(document_path)
        self.cache_dir = Path(cache_dir)

    def get_total_pages(self):
        raise NotImplementedError

    def render_page_dpi(self, page_number, dpi):
        raise NotImplementedError

    def render_page_fitted(self, page_number, target_width, target_height):
        raise NotImplementedError