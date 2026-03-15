from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


DEFAULT_CRASH_STATE_PATH = Path("state/crash_state.json")
RECOVERY_FAILURE_THRESHOLD = 3


@dataclass
class CrashState:
    last_clean_exit: bool = True
    consecutive_startup_failures: int = 0
    last_crash_reason: Optional[str] = None
    last_crash_phase: Optional[str] = None
    last_crash_time: Optional[str] = None
    recovery_required: bool = False


DEFAULT_CRASH_STATE = CrashState()


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _default_state() -> CrashState:
    return CrashState()


def _ensure_parent_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _normalize_bool(value: Any, default: bool) -> bool:
    if isinstance(value, bool):
        return value
    return default


def _normalize_int(value: Any, default: int, minimum: int = 0) -> int:
    if isinstance(value, bool):
        return default

    try:
        normalized = int(value)
    except (TypeError, ValueError):
        return default

    return max(minimum, normalized)


def _normalize_optional_str(value: Any) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, str):
        stripped = value.strip()
        return stripped or None
    return None


def _normalize_state(raw_state: Any) -> CrashState:
    if not isinstance(raw_state, dict):
        return _default_state()

    state = CrashState(
        last_clean_exit=_normalize_bool(
            raw_state.get("last_clean_exit"),
            DEFAULT_CRASH_STATE.last_clean_exit,
        ),
        consecutive_startup_failures=_normalize_int(
            raw_state.get("consecutive_startup_failures"),
            DEFAULT_CRASH_STATE.consecutive_startup_failures,
            minimum=0,
        ),
        last_crash_reason=_normalize_optional_str(raw_state.get("last_crash_reason")),
        last_crash_phase=_normalize_optional_str(raw_state.get("last_crash_phase")),
        last_crash_time=_normalize_optional_str(raw_state.get("last_crash_time")),
        recovery_required=_normalize_bool(
            raw_state.get("recovery_required"),
            DEFAULT_CRASH_STATE.recovery_required,
        ),
    )

    if state.consecutive_startup_failures >= RECOVERY_FAILURE_THRESHOLD:
        state.recovery_required = True

    return state


def load_crash_state(state_path: Path | str = DEFAULT_CRASH_STATE_PATH) -> CrashState:
    path = Path(state_path)

    if not path.exists():
        return _default_state()

    try:
        with path.open("r", encoding="utf-8") as handle:
            raw_state = json.load(handle)
    except (OSError, json.JSONDecodeError):
        return _default_state()

    return _normalize_state(raw_state)


def save_crash_state(
    state: CrashState,
    state_path: Path | str = DEFAULT_CRASH_STATE_PATH,
) -> None:
    path = Path(state_path)
    _ensure_parent_dir(path)

    temp_path = path.with_suffix(path.suffix + ".tmp")

    with temp_path.open("w", encoding="utf-8") as handle:
        json.dump(asdict(state), handle, indent=2)

    temp_path.replace(path)


def ensure_crash_state_file(state_path: Path | str = DEFAULT_CRASH_STATE_PATH) -> CrashState:
    path = Path(state_path)

    if path.exists():
        return load_crash_state(path)

    state = _default_state()
    save_crash_state(state, path)
    return state


def mark_app_start(
    state_path: Path | str = DEFAULT_CRASH_STATE_PATH,
) -> CrashState:
    state = load_crash_state(state_path)

    if state.last_clean_exit:
        state.consecutive_startup_failures = 0
    else:
        state.consecutive_startup_failures += 1

    state.last_clean_exit = False
    state.recovery_required = (
        state.consecutive_startup_failures >= RECOVERY_FAILURE_THRESHOLD
    )

    save_crash_state(state, state_path)
    return state


def mark_clean_exit(state_path: Path | str = DEFAULT_CRASH_STATE_PATH) -> CrashState:
    state = load_crash_state(state_path)
    state.last_clean_exit = True
    state.consecutive_startup_failures = 0
    state.recovery_required = False
    save_crash_state(state, state_path)
    return state


def record_crash(
    reason: Optional[str],
    phase: Optional[str],
    state_path: Path | str = DEFAULT_CRASH_STATE_PATH,
) -> CrashState:
    state = load_crash_state(state_path)
    state.last_clean_exit = False
    state.last_crash_reason = _normalize_optional_str(reason)
    state.last_crash_phase = _normalize_optional_str(phase)
    state.last_crash_time = _utc_now_iso()
    save_crash_state(state, state_path)
    return state


def clear_recovery_required(
    state_path: Path | str = DEFAULT_CRASH_STATE_PATH,
) -> CrashState:
    state = load_crash_state(state_path)
    state.recovery_required = False
    save_crash_state(state, state_path)
    return state


def reset_crash_state(state_path: Path | str = DEFAULT_CRASH_STATE_PATH) -> CrashState:
    state = _default_state()
    save_crash_state(state, state_path)
    return state
