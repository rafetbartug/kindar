from abc import ABC, abstractmethod
from pathlib import Path


class BaseDisplay(ABC):
    def __init__(self, width, height):
        self.width = width
        self.height = height

    @property
    def resolution(self):
        return self.width, self.height

    def validate_image_path(self, image_path):
        path = Path(image_path)
        if not path.exists() or not path.is_file():
            raise ValueError(f"Image file does not exist: {path}")
        return path

    @abstractmethod
    def show_image(self, image_path):
        raise NotImplementedError

    @abstractmethod
    def clear(self):
        raise NotImplementedError