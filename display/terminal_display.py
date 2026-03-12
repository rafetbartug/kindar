from display.base import BaseDisplay


class TerminalDisplay(BaseDisplay):
    def show_image(self, image_path):
        path = self.validate_image_path(image_path)

        print()
        print("--- DISPLAY OUTPUT ---")
        print("Backend    : terminal")
        print(f"Resolution : {self.width}x{self.height}")
        print(f"Image path : {path}")
        print("----------------------")

    def clear(self):
        print()
        print("--- DISPLAY CLEARED ---")