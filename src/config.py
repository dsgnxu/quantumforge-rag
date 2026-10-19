from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parents[1]

KNOWLEDGE_BASE_DIR = Path(os.getenv("KNOWLEDGE_BASE_DIR", ROOT / "knowledge_base"))
INDEX_DIR = Path(os.getenv("INDEX_DIR", ROOT / "index"))
INCOMING_DIR = Path(os.getenv("INCOMING_DIR", ROOT / "data" / "incoming"))
LOGS_DIR = Path(os.getenv("LOGS_DIR", ROOT / "logs"))

EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
)
LLM_MODE = os.getenv("LLM_MODE", "extractive")  # extractive | openai | yandex
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
YANDEX_API_KEY = os.getenv("YANDEX_API_KEY", "")
YANDEX_FOLDER_ID = os.getenv("YANDEX_FOLDER_ID", "")
YANDEX_MODEL = os.getenv("YANDEX_MODEL", "yandexgpt-lite")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

ENABLE_INJECTION_FILTER = os.getenv("ENABLE_INJECTION_FILTER", "true").lower() == "true"
ENABLE_SECURITY_PREPROMPT = (
    os.getenv("ENABLE_SECURITY_PREPROMPT", "true").lower() == "true"
)

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "800"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "120"))
TOP_K = int(os.getenv("TOP_K", "4"))
MIN_SCORE = float(os.getenv("MIN_SCORE", "0.35"))

FAISS_INDEX_PATH = INDEX_DIR / "faiss.index"
DOCS_STORE_PATH = INDEX_DIR / "docs.pkl"
META_PATH = INDEX_DIR / "meta.json"
QUERY_LOG_PATH = LOGS_DIR / "queries.jsonl"
UPDATE_LOG_PATH = LOGS_DIR / "index_update.log"
