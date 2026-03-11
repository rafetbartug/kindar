# KINDAR

Minimal embedded PDF & manga reader built on Raspberry Pi Zero 2 W.

## Vision

Kindar is designed as a single-purpose, stable e-ink reader device.
The goal is not a general-purpose Raspberry Pi project,
but a focused embedded system for distraction-free reading.

## Current Status

The core reader engine is functional.

### Implemented

- Headless Raspberry Pi OS setup
- Structured project architecture
- JSON-based reading state persistence
- Real PDF page detection (PyMuPDF)
- Grayscale render pipeline
- DPI testing modes (100 / 150 / 200)
- Fitted render mode for target e-ink resolution
- Cache system for rendered pages
- Memory usage monitoring
- File filtering (ignores empty/corrupted files)

## Architecture

kindar/
core/
reader.py
storage/
state_manager.py
ui/
menu.py
library/
cache/
state/

## Hardware Target

- Raspberry Pi Zero 2 W
- E-ink display (planned integration)
- Physical navigation buttons (planned)

