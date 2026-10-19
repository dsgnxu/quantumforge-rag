#!/usr/bin/env python3
"""Telegram-бот для тарифа Про (и опционально для демо)."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from src.config import TELEGRAM_BOT_TOKEN
from src.rag import ask

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("telegram_bot")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Привет! Я RAG-ассистент QuantumForge по базе Aether Nexus.\n"
        "Задайте вопрос о персонажах, планетах и технологиях."
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    question = (update.message.text or "").strip()
    if not question:
        return
    result = ask(question)
    text = result.answer
    if result.sources:
        text += "\n\nИсточники:\n- " + "\n- ".join(result.sources)
    await update.message.reply_text(text[:4000])


def main() -> None:
    if not TELEGRAM_BOT_TOKEN:
        raise SystemExit(
            "TELEGRAM_BOT_TOKEN не задан. Укажите токен в .env или переменной окружения."
        )
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    logger.info("Telegram bot started")
    app.run_polling()


if __name__ == "__main__":
    main()
