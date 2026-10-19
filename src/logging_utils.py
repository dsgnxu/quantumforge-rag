from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from src.config import LOGS_DIR, QUERY_LOG_PATH


def append_query_log(record: dict, path: Path | None = None) -> None:
    path = path or QUERY_LOG_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        **record,
    }
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def append_update_log(message: str, path: Path | None = None) -> None:
    from src.config import UPDATE_LOG_PATH

    path = path or UPDATE_LOG_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    with path.open("a", encoding="utf-8") as f:
        f.write(f"[{ts}] {message}\n")
