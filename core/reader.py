"""
Backward-compatible wrapper for legacy imports.

New code should import ReaderSession from core.session and open_reader
from core.reader_controller.
"""

from core.reader_controller import open_reader
from core.session import ReaderSession

__all__ = ["ReaderSession", "open_reader"]