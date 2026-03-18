from pathlib import Path
import subprocess

from display.base import BaseDisplay


class PreviewDisplay(BaseDisplay):
    def __init__(self, width, height, window_title="Kindar Preview"):
        super().__init__(width, height)
        self.window_title = window_title
        self._last_image_path = None

    def show_image(self, image_path):
        path = self.validate_image_path(image_path)

        if self._last_image_path == path:
            return

        subprocess.run(["open", str(path)], check=False)
        self._last_image_path = path

    def clear(self):
        self._last_image_path = None