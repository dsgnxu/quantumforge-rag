from __future__ import annotations

import json
import urllib.request

from src.config import (
    LLM_MODE,
    OPENAI_API_KEY,
    OPENAI_MODEL,
    YANDEX_API_KEY,
    YANDEX_FOLDER_ID,
    YANDEX_MODEL,
)
from src.prompts import extractive_answer


def generate(prompt: str, question: str, contexts: list[dict]) -> str:
    mode = (LLM_MODE or "extractive").lower()
    if mode == "openai" and OPENAI_API_KEY:
        return _openai_chat(prompt)
    if mode == "yandex" and YANDEX_API_KEY and YANDEX_FOLDER_ID:
        return _yandex_chat(prompt)
    return extractive_answer(question, contexts)


def _openai_chat(prompt: str) -> str:
    payload = {
        "model": OPENAI_MODEL,
        "messages": [
            {"role": "system", "content": "Follow the instructions in the user prompt."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
    }
    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENAI_API_KEY}",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data["choices"][0]["message"]["content"].strip()


def _yandex_chat(prompt: str) -> str:
    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    payload = {
        "modelUri": f"gpt://{YANDEX_FOLDER_ID}/{YANDEX_MODEL}",
        "completionOptions": {"stream": False, "temperature": 0.2, "maxTokens": 800},
        "messages": [{"role": "user", "text": prompt}],
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Api-Key {YANDEX_API_KEY}",
            "x-folder-id": YANDEX_FOLDER_ID,
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data["result"]["alternatives"][0]["message"]["text"].strip()
