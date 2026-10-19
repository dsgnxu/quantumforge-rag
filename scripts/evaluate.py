#!/usr/bin/env python3
"""Автопроверка RAG на golden set."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.rag import ask

GOLDEN_PATH = ROOT / "golden_questions.txt"
OUT_JSONL = ROOT / "logs" / "eval_results.jsonl"
OUT_CSV = ROOT / "logs" / "eval_results.csv"
REPORT = ROOT / "docs" / "coverage_report.md"


def load_golden(path: Path) -> list[dict]:
    items = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        # format: expect=yes|no|filter | question | keywords(optional,comma)
        parts = [p.strip() for p in line.split("|")]
        expect = parts[0].replace("expect=", "")
        question = parts[1]
        keywords = [k.strip().lower() for k in parts[2].split(",")] if len(parts) > 2 and parts[2] else []
        items.append({"expect": expect, "question": question, "keywords": keywords})
    return items


def judge(item: dict, answer: str, success: bool, filtered: bool) -> dict:
    expect = item["expect"]
    low = answer.lower()
    has_idk = "я не знаю" in low
    # достаточно попадания любого ключевого слова (OR), если их несколько через запятую
    kw_hit = (
        any(k in low for k in item["keywords"]) if item["keywords"] else True
    )

    if expect == "yes":
        ok = success and not has_idk and kw_hit
        reason = "answered with keywords" if ok else "expected answer missing"
    elif expect == "no":
        ok = has_idk or not success
        reason = "correctly unknown" if ok else "should not know"
    elif expect == "filter":
        ok = filtered or has_idk
        reason = "filtered/blocked" if ok else "security miss"
    else:
        ok = False
        reason = f"unknown expect={expect}"
    return {"ok": ok, "reason": reason}


def main() -> None:
    items = load_golden(GOLDEN_PATH)
    OUT_JSONL.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    gaps = []

    with OUT_JSONL.open("w", encoding="utf-8") as jf:
        for item in items:
            result = ask(item["question"], log=True)
            verdict = judge(item, result.answer, result.success, result.filtered)
            row = {
                "query": item["question"],
                "expect": item["expect"],
                "success_flag": result.success,
                "chunks_found": result.chunks_found,
                "filtered": result.filtered,
                "answer_length": len(result.answer),
                "sources": result.sources,
                "ok": verdict["ok"],
                "reason": verdict["reason"],
                "answer": result.answer,
            }
            jf.write(json.dumps(row, ensure_ascii=False) + "\n")
            rows.append(row)
            if not verdict["ok"] or item["expect"] in {"no", "filter"}:
                gaps.append(row)

    with OUT_CSV.open("w", encoding="utf-8", newline="") as cf:
        writer = csv.DictWriter(
            cf,
            fieldnames=[
                "query",
                "expect",
                "ok",
                "reason",
                "chunks_found",
                "filtered",
                "answer_length",
                "sources",
            ],
        )
        writer.writeheader()
        for r in rows:
            writer.writerow(
                {
                    "query": r["query"],
                    "expect": r["expect"],
                    "ok": r["ok"],
                    "reason": r["reason"],
                    "chunks_found": r["chunks_found"],
                    "filtered": r["filtered"],
                    "answer_length": r["answer_length"],
                    "sources": ";".join(r["sources"]),
                }
            )

    total = len(rows)
    passed = sum(1 for r in rows if r["ok"])
    missing_topics = [r["query"] for r in rows if r["expect"] == "no"]
    failed = [r for r in rows if not r["ok"]]

    report = f"""# Отчёт о покрытии базы знаний (Задание 7)

## Сводка
- Всего golden-вопросов: {total}
- Успешно по ожиданию: {passed}/{total}
- Выявленных пробелов (expect=no): {len(missing_topics)}

## Темы с пробелами
"""
    for q in missing_topics:
        report += f"- {q}\n"

    report += "\n## Ошибки / неожиданное поведение\n"
    if not failed:
        report += "- Нет\n"
    else:
        for r in failed:
            report += f"- [{r['expect']}] {r['query']} → {r['reason']}\n"

    report += """
## Рекомендации для QuantumForge Software
1. Назначить владельцев (CODEOWNERS) для каждой сущности базы знаний.
2. Добавлять документы по темам из «пробелов» golden-набора до деплоя.
3. Держать nightly `evaluate.py` в CI: падение recall/coverage блокирует релиз индекса.
4. Для SOC 2 — журналировать sources каждого ответа (уже в `logs/queries.jsonl`).
"""
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(report, encoding="utf-8")
    print(report)
    print(f"\nSaved: {OUT_JSONL}, {OUT_CSV}, {REPORT}")


if __name__ == "__main__":
    main()
