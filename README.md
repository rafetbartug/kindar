# KINDAR

      _  ___ _   _ ____    _    ____
     | |/ (_) \ | |  _ \  / \  |  _ \
     | ' /| |  \| | | | |/ _ \ | |_) |
     | . \| | |\  | |_| / ___ \|  _ <
     |_|\_\_|_| \_|____/_/   \_\_| \_\

        .-------------------------------------.
       /   minimal embedded e-ink reader      /
      /   pdf + cbz • raspberry pi zero 2 w  /
     '-------------------------------------'

              .~.                           .~.
             /   \_________________________/   \
            |                                     |
            |        raspberry pi zero 2 w        |
            |_____________________________________|
                 \_  _/                 \_  _/
                   ||                     ||
                   ||                     ||

Minimal embedded PDF and manga reader built for Raspberry Pi Zero 2 W.

## Vision

Kindar is a single-purpose reading device.
It is designed with an embedded-systems mindset:
minimal, predictable, stable, and distraction-free.

The Raspberry Pi is treated as a firmware-like platform for a dedicated e-ink reader,
not as a general-purpose computer.

## Current Status

The core reading stack is working and has been refactored into cleaner components.

### Implemented

- Headless Raspberry Pi OS setup
- Structured modular project architecture
- JSON-based reading state persistence
- Safe state migration and normalization
- Atomic state writes for better reliability
- Real PDF page detection and rendering with PyMuPDF
- Real CBZ archive support
- Natural page ordering for CBZ image entries
- Grayscale render pipeline
- DPI render modes (100 / 150 / 200)
- Fitted render mode for target e-ink resolution
- Cache system for rendered pages
- Memory usage monitoring
- File filtering for supported formats only
- Category-based library filtering
- Display abstraction layer
- Terminal display backend
- E-ink display backend skeleton

## Supported Formats

- Books: `.pdf`
- Manga: `.cbz`

## Architecture

```text
kindar/
├── main.py
├── core/
│   ├── reader.py              # legacy compatibility wrapper
│   ├── session.py             # reader session orchestration
│   └── documents/
│       ├── base.py            # document interface
│       ├── pdf_document.py    # PDF implementation
│       ├── cbz_document.py    # CBZ implementation
│       └── factory.py         # document selection
├── display/
│   ├── base.py                # display interface
│   ├── terminal_display.py    # terminal backend
│   └── eink_display.py        # e-ink backend skeleton
├── library/
│   ├── books/
│   ├── manga/
│   └── catalog.py             # library listing and filtering
├── storage/
│   └── state_manager.py       # persistence and recovery
├── ui/
│   └── menu.py                # terminal UI only
├── cache/
├── state/
└── logs/
```

## Design Direction

Kindar is being developed with software design principles in mind.
Current refactoring direction emphasizes:

- Single Responsibility Principle
- Clear separation between UI, session orchestration, persistence, and rendering
- Strategy-style document handling for PDF and CBZ
- Adapter-style display backends for terminal and future e-ink hardware
- Dependency injection for display selection
- Fail-soft behavior for embedded stability

## Display Backends

Display backend selection is controlled from the application entry point.
The backend can be selected with the `KINDAR_DISPLAY` environment variable.

### Terminal backend

```bash
KINDAR_DISPLAY=terminal python3 main.py
```

### E-ink backend skeleton

```bash
KINDAR_DISPLAY=eink python3 main.py
```

At the moment, the e-ink backend is only a structural placeholder and is not yet connected to real hardware.

## Hardware Target

- Raspberry Pi Zero 2 W
- E-ink display (integration in progress)
- Physical navigation buttons (planned)
- Embedded boot-to-reader flow (planned)

## Near-Term Roadmap

- Real e-ink backend implementation
- Physical button input integration
- Android to Pi file transfer flow
- Boot directly into reader mode
- Embedded stability hardening and power management