

from display.base import BaseDisplay


class EinkDisplay(BaseDisplay):
    def show_image(self, image_path):
        path = self.validate_image_path(image_path)
        raise NotImplementedError(
            f"E-ink display backend is not implemented yet. Image ready at: {path}"
        )

    def clear(self):
        raise NotImplementedError("E-ink display backend is not implemented yet.")