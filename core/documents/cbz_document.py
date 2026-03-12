

from io import BytesIO
from pathlib import Path
import re
import zipfile

from PIL import Image

from core.documents.base import BaseDocument


def natural_sort_key(value):
    parts = re.split(r"(\d+)", value.lower())
    return [int(part) if part.isdigit() else part for part in parts]


class CbzDocument(BaseDocument):
    IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif"}

    def __init__(self, document_path, cache_dir):
        super().__init__(document_path, cache_dir)
        self.image_entries = self._load_image_entries()

    def _load_image_entries(self):
        if not self.document_path.exists():
            raise ValueError(f"File not found: {self.document_path}")

        try:
            with zipfile.ZipFile(self.document_path, "r") as archive:
                names = []
                for name in archive.namelist():
                    path = Path(name)

                    if path.name.startswith("."):
                        continue

                    if path.suffix.lower() not in self.IMAGE_EXTENSIONS:
                        continue

                    names.append(name)

                names.sort(key=natural_sort_key)

                if not names:
                    raise ValueError("CBZ contains no supported image files.")

                return names
        except ValueError:
            raise
        except zipfile.BadZipFile:
            raise ValueError("Invalid CBZ archive.")
        except Exception as e:
            raise ValueError(f"Cannot open CBZ: {e}")

    def get_total_pages(self):
        return len(self.image_entries)

    def _load_image(self, page_number):
        if page_number < 1 or page_number > len(self.image_entries):
            raise ValueError("Invalid CBZ page number.")

        entry_name = self.image_entries[page_number - 1]

        try:
            with zipfile.ZipFile(self.document_path, "r") as archive:
                raw_data = archive.read(entry_name)

            image = Image.open(BytesIO(raw_data))
            image.load()
            return image
        except ValueError:
            raise
        except Exception as e:
            raise ValueError(f"Cannot load CBZ image '{entry_name}': {e}")

    def render_page_dpi(self, page_number, dpi):
        image = self._load_image(page_number).convert("L")

        output_path = self.cache_dir / f"page_{page_number:04d}_{dpi}dpi.png"
        image.save(output_path, "PNG")

        return {
            "output_path": output_path,
            "width": image.width,
            "height": image.height,
            "mode": "DPI-like render (source image grayscale)",
            "extra": {
                "dpi": dpi,
                "note": "CBZ source images are cached directly in grayscale.",
            },
        }

    def render_page_fitted(self, page_number, target_width, target_height):
        image = self._load_image(page_number).convert("L")

        fitted = image.copy()
        fitted.thumbnail((target_width, target_height), Image.Resampling.LANCZOS)

        output_path = self.cache_dir / (
            f"page_{page_number:04d}_fit_{target_width}x{target_height}.png"
        )
        fitted.save(output_path, "PNG")

        return {
            "output_path": output_path,
            "width": fitted.width,
            "height": fitted.height,
            "mode": "fitted render",
            "extra": {
                "target_width": target_width,
                "target_height": target_height,
                "source_width": image.width,
                "source_height": image.height,
            },
        }