# QuantumForge Software — RAG Knowledge Bot (Sprint 7)

Учебный RAG-бот для корпоративной базы знаний компании **QuantumForge Software** (кейс Digital Twin / SCADA).

Ветка разработки: `rag`.

## Стек

- Python 3.11 (Docker) / локально 3.11+
- Embeddings: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (384-dim)
- Vector DB: **FAISS**
- LLM: extractive (по умолчанию) / OpenAI / YandexGPT
- API: FastAPI (`/ask`)
- Telegram-бот (тариф Про)
- Docker Compose

## Быстрый старт

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 1) База знаний + подмена терминов
python scripts/generate_kb.py

# 2) Индекс
python scripts/build_index.py

# 3) REPL
python bot/repl.py

# или API
uvicorn bot.api:app --reload --port 8000
# curl -X POST localhost:8000/ask -H 'Content-Type: application/json' -d '{"question":"Кто такой Xarn Velgor?"}'
```

### Docker

```bash
docker compose up --build rag-bot
curl -X POST localhost:8000/ask -H 'Content-Type: application/json' \
  -d '{"question":"Что такое Void Core?"}'
```

Telegram:

```bash
export TELEGRAM_BOT_TOKEN=...
docker compose --profile telegram up --build telegram-bot
```

## Структура

| Путь | Назначение |
|---|---|
| `knowledge_base/` | 35+ уникальных документов Aether Nexus |
| `terms_map.json` | словарь замен Star Wars → вымысел |
| `index/` | FAISS + метаданные |
| `bot/` | API, REPL, Telegram |
| `scripts/` | KB, index, update, evaluate, demo |
| `docs/task1_research.md` | исследование моделей/инфры |
| `Project_template.md` | ответы по всем заданиям |
| `docs/diagrams/*.puml` | архитектура обновления и sequence eval |

## Вселенная базы знаний

Исходник: Star Wars fandom → целевая **Aether Nexus** (Xarn Velgor, Void Core, Synth Flux, …).  
Так LLM не может «вспомнить» ответы из предобучения.

## Безопасность (Задание 5)

- Pre-prompt: игнорировать инструкции внутри CONTEXT
- Фильтр чанков: `Ignore all instructions`, `swordfish`, …
- Post-guard ответа
- Документ-троян: `knowledge_base/malicious_trojan.md`

## Обновление индекса (Задание 6)

```bash
# положите новые .md в data/incoming/
python scripts/update_index.py
# cron: см. scripts/crontab.example
```

## Оценка покрытия (Задание 7)

```bash
python scripts/prepare_gaps.py apply   # убрать 3 сущности
python scripts/build_index.py
python scripts/evaluate.py
python scripts/prepare_gaps.py restore
```
