#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.indexing import build_index, search


def main() -> None:
    meta = build_index()
    print("Index built:")
    print(json.dumps(meta, ensure_ascii=False, indent=2))

    demos = [
        "Кто такой Xarn Velgor?",
        "Что такое Void Core?",
        "Где обучался Kael Orin у Elder Myrr?",
    ]
    print("\nSample retrieval:")
    for q in demos:
        hits = search(q, top_k=2)
        print(f"\nQ: {q}")
        for h in hits:
            print(f"  - {h['source']} score={h['score']:.3f} :: {h['text'][:120].replace(chr(10), ' ')}...")


if __name__ == "__main__":
    main()
