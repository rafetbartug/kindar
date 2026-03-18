

from __future__ import annotations

import resource
import time
from dataclasses import dataclass, asdict
from pathlib import Path
import csv
from typing import Optional


DEFAULT_METRICS_CSV_PATH = Path("logs/render_metrics.csv")


@dataclass
class RenderMetrics:
    document_type: str
    render_mode: str
    page: int
    target_width: int
    target_height: int
    cache_hit: bool
    memory_before_kb: int
    memory_after_kb: int
    delta_kb: int
    elapsed_ms: int
    status: str
    error: Optional[str] = None


def get_rss_kb() -> int:
    usage = resource.getrusage(resource.RUSAGE_SELF)
    return int(usage.ru_maxrss)


def now_perf_ms() -> int:
    return int(time.perf_counter() * 1000)


def build_render_metrics(
    document_type: str,
    render_mode: str,
    page: int,
    target_width: int,
    target_height: int,
    cache_hit: bool,
    memory_before_kb: int,
    memory_after_kb: int,
    elapsed_ms: int,
    status: str,
    error: Optional[str] = None,
) -> RenderMetrics:
    delta_kb = memory_after_kb - memory_before_kb

    return RenderMetrics(
        document_type=document_type,
        render_mode=render_mode,
        page=page,
        target_width=target_width,
        target_height=target_height,
        cache_hit=cache_hit,
        memory_before_kb=memory_before_kb,
        memory_after_kb=memory_after_kb,
        delta_kb=delta_kb,
        elapsed_ms=elapsed_ms,
        status=status,
        error=error,
    )


def append_render_metrics_csv(
    metrics: RenderMetrics,
    csv_path: Path | str = DEFAULT_METRICS_CSV_PATH,
) -> None:
    path = Path(csv_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    row = asdict(metrics)
    write_header = not path.exists() or path.stat().st_size == 0

    with path.open("a", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(row.keys()))
        if write_header:
            writer.writeheader()
        writer.writerow(row)