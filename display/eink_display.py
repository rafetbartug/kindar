from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageOps, ImageFilter

from display.base import BaseDisplay

WAVESHARE_LIB = "/home/rbb/e-Paper/RaspberryPi_JetsonNano/python/lib"
if WAVESHARE_LIB not in sys.path:
    sys.path.append(WAVESHARE_LIB)

from waveshare_epd import epd7in5_V2


class EinkDisplay(BaseDisplay):
    def __init__(
        self,
        rotate_degrees: int = 90,
        contrast: float = 1.15,
        threshold: int = 185,
        sharpen: bool = True,
    ):
        self.rotate_degrees = rotate_degrees
        self.contrast = contrast
        self.threshold = threshold
        self.sharpen = sharpen
        self._epd = epd7in5_V2.EPD()
        self.width = self._epd.width
        self.height = self._epd.height
        self._is_awake = False
        self.keep_awake = True

    def _ensure_awake(self):
        if not self._is_awake:
            self._epd.init()
            self._is_awake = True

    def sleep(self):
        if self._is_awake:
            self._epd.sleep()
            self._is_awake = False

    def _to_1bit(self, image: Image.Image) -> Image.Image:
        image = ImageOps.autocontrast(image)

        if self.sharpen:
            image = image.filter(ImageFilter.SHARPEN)

        if self.contrast != 1.0:
            midpoint = 128
            image = image.point(
                lambda p: max(0, min(255, int((p - midpoint) * self.contrast + midpoint)))
            )

        return image.point(lambda p: 255 if p > self.threshold else 0, mode="1")

    def _prepare_frame(self, image: Image.Image) -> Image.Image:
        image = ImageOps.exif_transpose(image).convert("L")

        if self.rotate_degrees:
            image = image.rotate(self.rotate_degrees, expand=True)

        ratio = min(self.width / image.width, self.height / image.height)
        new_width = max(1, int(image.width * ratio))
        new_height = max(1, int(image.height * ratio))
        image = image.resize((new_width, new_height), Image.LANCZOS)

        canvas = Image.new("L", (self.width, self.height), 255)
        x = (self.width - new_width) // 2
        y = (self.height - new_height) // 2
        canvas.paste(image, (x, y))

        return self._to_1bit(canvas)

    def show_image(self, image_path):
        path = Path(self.validate_image_path(image_path))
        image = Image.open(path)
        frame = self._prepare_frame(image)

        self._ensure_awake()
        self._epd.display(self._epd.getbuffer(frame))
        if not self.keep_awake:
            self.sleep()

    def clear(self):
        self._ensure_awake()
        self._epd.Clear()
        self.sleep()