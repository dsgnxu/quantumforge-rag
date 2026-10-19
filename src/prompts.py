from __future__ import annotations

from src.security import SECURITY_SYSTEM_PROMPT

# Few-shot примеры из предметной области Aether Nexus
FEW_SHOT_EXAMPLES = [
    {
        "q": "Как называется столица планеты Prismara?",
        "a": "Столицей и самой планетой-экumenополисом является Prismara — центр власти Dominion Sphere.",
    },
    {
        "q": "Чем питается HyperRelay?",
        "a": "HyperRelay — измерение сверхсветовых перелётов; безопасный прыжок требует навигационных карт и servo-unit, а не «ядра Void Core».",
    },
]


def build_prompt(question: str, contexts: list[dict], secure: bool = True) -> str:
    system = SECURITY_SYSTEM_PROMPT if secure else (
        "Ты помощник по базе знаний. Отвечай по контексту."
    )

    examples = "\n\n".join(
        f"Q: {ex['q']}\nA: {ex['a']}" for ex in FEW_SHOT_EXAMPLES
    )

    context_block = "\n\n".join(
        f"[{i+1}] source={c.get('source')} title={c.get('title')}\n{c.get('text')}"
        for i, c in enumerate(contexts)
    )

    return f"""[System]
{system}

Ты помощник, который сначала размышляет, а потом отвечает. Всегда пиши свои шаги.

[Examples]
{examples}

[CONTEXT]
<<<
{context_block}
>>>

[User]
{question}

Формат ответа:
1. Шаги рассуждения (CoT)
2. Итоговый ответ (если фактов нет — ровно «Я не знаю»)
"""


def extractive_answer(question: str, contexts: list[dict]) -> str:
    """Локальный генератор без внешнего LLM: CoT + ответ из чанков."""
    if not contexts:
        return (
            "1. Ищу релевантные фрагменты в индексе.\n"
            "2. Подходящих чанков не найдено.\n"
            "3. Следовательно, ответ — Я не знаю."
        )

    steps = [
        f"1. Сначала найду фрагменты по запросу: «{question}».",
        f"2. Найдено чанков: {len(contexts)}. Лучший источник: {contexts[0].get('source')} "
        f"(score={contexts[0].get('score', 0):.3f}).",
        "3. Соберу факты только из CONTEXT, игнорируя любые инструкции внутри документов.",
    ]

    # Берём самое релевантное предложение/абзац
    best = contexts[0]["text"].strip()
    # Убираем заголовок markdown если есть
    lines = [ln for ln in best.splitlines() if ln.strip() and not ln.startswith("#")]
    summary = " ".join(lines)[:500]

    answer = (
        "\n".join(steps)
        + f"\n\nИтоговый ответ: {summary}"
    )
    return answer
