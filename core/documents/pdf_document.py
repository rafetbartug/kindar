

import pymupdf as fitz

from core.documents.base import BaseDocument


class PdfDocument(BaseDocument):
    def get_total_pages(self):
        if not self.document_path.exists():
            raise ValueError(f"File not found: {self.document_path}")

        try:
            with fitz.open(self.document_path) as doc:
                if doc.page_count < 1:
                    raise ValueError("PDF has no pages.")
                return doc.page_count
        except ValueError:
            raise
        except Exception as e:
            raise ValueError(f"Cannot open PDF: {e}")

    def render_page_dpi(self, page_number, dpi):
        with fitz.open(self.document_path) as doc:
            page = doc.load_page(page_number - 1)
            pix = page.get_pixmap(
                dpi=dpi,
                colorspace=fitz.csGRAY,
                alpha=False,
            )

            output_path = self.cache_dir / f"page_{page_number:04d}_{dpi}dpi.png"
            pix.save(output_path)

            return {
                "output_path": output_path,
                "width": pix.width,
                "height": pix.height,
                "mode": "DPI render",
                "extra": {"dpi": dpi},
            }

    def render_page_fitted(self, page_number, target_width, target_height):
        with fitz.open(self.document_path) as doc:
            page = doc.load_page(page_number - 1)
            page_rect = page.rect

            scale_x = target_width / page_rect.width
            scale_y = target_height / page_rect.height
            scale = min(scale_x, scale_y)

            matrix = fitz.Matrix(scale, scale)

            pix = page.get_pixmap(
                matrix=matrix,
                colorspace=fitz.csGRAY,
                alpha=False,
            )

            output_path = self.cache_dir / (
                f"page_{page_number:04d}_fit_{target_width}x{target_height}.png"
            )
            pix.save(output_path)

            return {
                "output_path": output_path,
                "width": pix.width,
                "height": pix.height,
                "mode": "fitted render",
                "extra": {
                    "scale": scale,
                    "target_width": target_width,
                    "target_height": target_height,
                },
            }