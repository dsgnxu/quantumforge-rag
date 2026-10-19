#!/usr/bin/env python3
"""Ежедневное обновление индекса: сканирует data/incoming и knowledge_base."""

from __future__ import annotations

import hashlib
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.config import INCOMING_DIR, INDEX_DIR, KNOWLEDGE_BASE_DIR
from src.indexing import build_index
from src.logging_utils import append_update_log

STATE_PATH = INDEX_DIR / "update_state.json"


def file_fingerprint(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    h.update(str(path.stat().st_mtime_ns).encode())
    return h.hexdigest()


def load_state() -> dict:
    if STATE_PATH.exists():
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    return {"files": {}}


def save_state(state: dict) -> None:
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def ingest_incoming() -> list[str]:
    """Копирует новые/изменённые файлы из data/incoming в knowledge_base."""
    INCOMING_DIR.mkdir(parents=True, exist_ok=True)
    KNOWLEDGE_BASE_DIR.mkdir(parents=True, exist_ok=True)
    added = []
    for path in sorted(INCOMING_DIR.glob("*.md")):
        dest = KNOWLEDGE_BASE_DIR / path.name
        if not dest.exists() or dest.read_bytes() != path.read_bytes():
            shutil.copy2(path, dest)
            added.append(path.name)
    return added


def changed_kb_files(state: dict) -> list[str]:
    changed = []
    current = {}
    for path in sorted(KNOWLEDGE_BASE_DIR.glob("*.md")):
        if path.name.lower() == "readme.md":
            continue
        fp = file_fingerprint(path)
        current[path.name] = fp
        if state.get("files", {}).get(path.name) != fp:
            changed.append(path.name)
    state["files"] = current
    return changed


def main() -> None:
    started = datetime.now(timezone.utc).isoformat()
    append_update_log(f"update started at {started}")
    try:
        incoming = ingest_incoming()
        state = load_state()
        changed = changed_kb_files(state)
        if not changed and not incoming:
            append_update_log("no changes detected, index rebuild skipped")
            print("No changes. Skip rebuild.")
            # всё равно можно форсировать: раскомментируйте следующую строку
            # meta = build_index()
            save_state(state)
            return

        meta = build_index()
        save_state(state)
        msg = (
            f"index updated at {datetime.now(timezone.utc).date()}, "
            f"{len(incoming)} files added from incoming, "
            f"{len(changed)} kb files changed, "
            f"chunks={meta['chunk_count']}, "
            f"0 errors"
        )
        append_update_log(msg)
        print(msg)
        print(json.dumps(meta, ensure_ascii=False, indent=2))
    except Exception as exc:  # noqa: BLE001
        append_update_log(f"ERROR: {exc}")
        raise


if __name__ == "__main__":
    main()
