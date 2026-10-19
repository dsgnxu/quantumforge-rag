from __future__ import annotations

import re
from dataclasses import dataclass

from src.config import (
    ENABLE_INJECTION_FILTER,
    ENABLE_SECURITY_PREPROMPT,
    MIN_SCORE,
    TOP_K,
)
from src.indexing import search
from src.llm import generate
from src.logging_utils import append_query_log
from src.prompts import build_prompt
from src.security import filter_chunks, looks_like_injection

# Латинские имена сущностей в запросе (Aether Nexus / вымысел)
ENTITY_RE = re.compile(r"\b[A-Z][A-Za-z0-9\-]{2,}\b")


def _entities(text: str) -> set[str]:
    return {m.group(0).lower() for m in ENTITY_RE.finditer(text or "")}


def _chunks_support_entities(question: str, chunks: list[dict]) -> bool:
    """Имена сущностей из вопроса должны подтверждаться чанками.

    Для длинных токенов (>=5) требуем, чтобы ВСЕ встретились в контексте —
    иначе семантический поиск цепляет соседние планеты/биографии.
    """
    ents = {e for e in _entities(question) if len(e) >= 5}
    if not ents:
        return True
    blob = " ".join(c.get("text", "") for c in chunks).lower()
    return all(e in blob for e in ents)


@dataclass
class RagResult:
    answer: str
    sources: list[str]
    chunks_found: bool
    filtered: bool
    success: bool
    retrieved: list[dict]


def ask(
    question: str,
    top_k: int = TOP_K,
    min_score: float = MIN_SCORE,
    enable_filter: bool | None = None,
    enable_preprompt: bool | None = None,
    log: bool = True,
) -> RagResult:
    enable_filter = ENABLE_INJECTION_FILTER if enable_filter is None else enable_filter
    enable_preprompt = (
        ENABLE_SECURITY_PREPROMPT if enable_preprompt is None else enable_preprompt
    )

    # Прямой вредоносный запрос пользователя
    if enable_filter and looks_like_injection(question):
        answer = (
            "1. Запрос содержит признаки prompt-injection / запроса секретов.\n"
            "2. Фильтр безопасности отклоняет генерацию.\n"
            "3. Итоговый ответ: Я не знаю."
        )
        result = RagResult(
            answer=answer,
            sources=[],
            chunks_found=False,
            filtered=True,
            success=False,
            retrieved=[],
        )
        if log:
            _log(question, result)
        return result

    retrieved = search(question, top_k=top_k)
    retrieved = [c for c in retrieved if c.get("score", 0) >= min_score]

    filtered_flag = False
    if enable_filter:
        retrieved, blocked = filter_chunks(retrieved)
        filtered_flag = bool(blocked)

    # Семантический «шум»: похожие документы, но без упоминания сущностей из вопроса
    if retrieved and not _chunks_support_entities(question, retrieved):
        retrieved = []

    if not retrieved:
        answer = (
            "1. Ищу информацию в векторном индексе.\n"
            "2. Релевантных безопасных фрагментов нет"
            + (" (сработал фильтр вредоносных чанков)" if filtered_flag else "")
            + ".\n"
            "3. Итоговый ответ: Я не знаю."
        )
        result = RagResult(
            answer=answer,
            sources=[],
            chunks_found=False,
            filtered=filtered_flag,
            success=False,
            retrieved=[],
        )
        if log:
            _log(question, result)
        return result

    prompt = build_prompt(question, retrieved, secure=enable_preprompt)
    answer = generate(prompt, question, retrieved)

    # Post-check: не пропускаем явный секрет в ответе
    if enable_filter and looks_like_injection(answer):
        answer = (
            "1. Модель/контекст попытались раскрыть запрещённые данные.\n"
            "2. Post-generation guard заблокировал ответ.\n"
            "3. Итоговый ответ: Я не знаю."
        )
        result = RagResult(
            answer=answer,
            sources=[c.get("source", "") for c in retrieved],
            chunks_found=True,
            filtered=True,
            success=False,
            retrieved=retrieved,
        )
        if log:
            _log(question, result)
        return result

    success = "я не знаю" not in answer.lower()
    result = RagResult(
        answer=answer,
        sources=[c.get("source", "") for c in retrieved],
        chunks_found=True,
        filtered=filtered_flag,
        success=success,
        retrieved=retrieved,
    )
    if log:
        _log(question, result)
    return result


def _log(question: str, result: RagResult) -> None:
    append_query_log(
        {
            "query": question,
            "chunks_found": result.chunks_found,
            "answer_length": len(result.answer),
            "success": result.success,
            "filtered": result.filtered,
            "sources": result.sources,
            "answer_preview": result.answer[:300],
        }
    )
