#!/usr/bin/env python3
"""Задание 7: искусственные пробелы — убрать 2–3 ключевые сущности."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KB = ROOT / "knowledge_base"
GAPS = ROOT / "knowledge_base_gaps"

# По заданию: убрать Void Core, Xarn Velgor, Synth Flux
GAP_FILES = ["void_core.md", "xarn_velgor.md", "synth_flux.md"]


def main() -> None:
    action = (sys.argv[1] if len(sys.argv) > 1 else "apply").lower()
    GAPS.mkdir(parents=True, exist_ok=True)

    if action == "apply":
        for name in GAP_FILES:
            src = KB / name
            if src.exists():
                shutil.move(str(src), str(GAPS / name))
                print(f"moved {name} → knowledge_base_gaps/")
        print("Gaps applied. Rebuild index: python scripts/build_index.py")
    elif action == "restore":
        for name in GAP_FILES:
            src = GAPS / name
            if src.exists():
                shutil.move(str(src), str(KB / name))
                print(f"restored {name}")
        print("Gaps restored. Rebuild index: python scripts/build_index.py")
    else:
        raise SystemExit("Usage: prepare_gaps.py [apply|restore]")


if __name__ == "__main__":
    main()
