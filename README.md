# KINDAR

       .~~.   .~~.
      '. \ ' ' / .'
       .~ .~~~..~.                      _                          _
      : .~.'~'.~. :   ___ ___ ___ ___| |_ ___ ___ ___ _ _    ___|_|
     ~ (   ) (   ) ~ |  _| .'|_ -| . | . | -_|  _|  _| | |  | . | |
    ( : '~'.~.'~' : )|_| |__,|___|  _|___|___|_| |_| |_  |  |  _|_|
     ~ .~ (   ) ~. ~             |_|                 |___|  |_|
      (  : '~' :  )
       '~ .~~~. ~'
           '~'

Minimal **embedded PDF and manga reader** built for **Raspberry Pi Zero 2 W**.

Kindar is a lightweight reading device prototype designed with an **embedded systems mindset**.  
The project focuses on **simplicity, stability, and deterministic behavior** rather than feature-heavy software.

---

# Project Goals

Kindar aims to explore how a small Linux SBC can be turned into a **single‑purpose embedded device**.

Core design goals:

- Minimal and distraction‑free reading environment
- Stable long‑running operation
- Predictable system behavior
- Low memory footprint
- Clean modular architecture

Instead of treating the Raspberry Pi as a general computer, Kindar treats it as a **firmware platform powering a dedicated device**.

---

# Key Engineering Highlights

This project intentionally focuses on **systems engineering practices** that are valuable for embedded or low‑level software development.

Highlights include:

- Modular architecture with clear subsystem boundaries
- Document abstraction layer supporting multiple formats
- Display abstraction supporting multiple rendering targets
- Atomic state persistence for crash safety
- Render caching system for performance on low‑power hardware
- Embedded‑friendly fail‑soft behavior
- Headless Linux device workflow

These design choices make Kindar closer to a **device firmware stack** than a typical Python application.

---

# Current Status

The core reading stack is implemented and functional, including direct e‑ink output on the target hardware.

### Implemented

System setup

- Headless Raspberry Pi OS environment
- SSH‑based device management
- Modular project structure

Reader functionality

- Real PDF rendering via **PyMuPDF**
- Real CBZ archive support
- Natural page ordering for CBZ image entries
- Page boundary enforcement
- Resume from last read page

Rendering pipeline

- Grayscale render pipeline
- Multiple DPI render modes (`100 / 150 / 200`)
- Fitted render mode for e‑ink resolution
- Rendered page caching
- Memory usage monitoring
- Automatic page render on navigation
- Per-session render mode selection (`r100 / r150 / r200 / rf`)

Persistence

- JSON‑based reading state
- Atomic state writes
- Safe state normalization
- Crash‑safe persistence

Library system

- Category‑based browsing
- File filtering for supported formats
- Protection against invalid files

Architecture

- Document abstraction layer
- Display abstraction layer
- Terminal display backend
- Waveshare 7.5" e‑ink display backend
- Session-level render mode control

---

# Supported Formats

Books

```
.pdf
```

Manga

```
.cbz
```

---

# Architecture

```
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
│   └── eink_display.py        # Waveshare e‑ink backend
├── library/
│   ├── books/
│   ├── manga/
│   └── catalog.py             # library listing
├── storage/
│   └── state_manager.py       # persistence + recovery
├── ui/
│   └── menu.py                # terminal UI
├── cache/
├── state/
└── logs/
```

The architecture separates responsibilities into several independent layers:

- **Document layer** – parsing and rendering logic
- **Session layer** – reading flow orchestration
- **Display layer** – output backends
- **Persistence layer** – state storage and recovery
- **UI layer** – user interaction

This structure makes the system easier to maintain and adapt to other embedded devices.

---

# Reader Controls

Current reader controls:

- `n` – next page and auto-render using the currently selected render mode
- `p` – previous page and auto-render using the currently selected render mode
- `m` – cycle render mode for the current session
- `r` / `rf` / `r100` / `r150` / `r200` – manual render commands
- `q` – save progress, clear the display to white, and sleep the panel

Default render behavior:

- Books default to `r100`
- Manga defaults to `r150`

The selected render mode persists for the current reading session and is reused by page navigation.

---

# Display Backends

Display backend selection is controlled via the `KINDAR_DISPLAY` environment variable.

### Terminal backend

```
KINDAR_DISPLAY=terminal python3 main.py
```

Used primarily for development and debugging.

### E‑ink backend

```
KINDAR_DISPLAY=eink python3 main.py
```

The e‑ink backend is now connected to the Waveshare 7.5" display driver and can render real pages directly to the panel.

Current behavior:

- Rendered pages are pushed directly to the e‑ink display
- Navigation commands can auto-render the next/previous page
- Reader sessions can cycle render quality modes during reading
- Exiting the reader clears the panel to white and puts the display into sleep mode

---

# Hardware Target

Primary device platform:

- Raspberry Pi Zero 2 W
- Waveshare 7.5" e‑ink display
- Physical navigation buttons (planned)

Design goals for the device:

- Boot directly into reader mode
- Minimal power consumption
- Stable long‑running operation

---

# Development Roadmap

Near‑term milestones

- E‑ink display quality and refresh tuning
- GPIO‑based physical navigation buttons
- Android → Raspberry Pi file transfer workflow
- Automatic boot directly into reader mode
- Embedded stability hardening
- Power management improvements

Future directions

- Improved caching strategies
- Performance optimizations for low‑power CPUs
- Better display refresh control for e‑ink panels
- Possible extraction of a reusable document rendering engine

---


# Author

Rafet Bartuğ

Software Engineering student exploring embedded systems, low‑power computing, and minimal device design.
