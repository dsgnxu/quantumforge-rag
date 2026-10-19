FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1 \
    LLM_MODE=extractive \
    ENABLE_INJECTION_FILTER=true \
    ENABLE_SECURITY_PREPROMPT=true \
    EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 \
    KNOWLEDGE_BASE_DIR=/app/knowledge_base \
    INDEX_DIR=/app/index \
    LOGS_DIR=/app/logs \
    INCOMING_DIR=/app/data/incoming \
    HF_HOME=/app/.cache/huggingface

# Строим индекс при сборке образа (офлайн-демо)
RUN python scripts/generate_kb.py && \
    python scripts/build_index.py

EXPOSE 8000

CMD ["uvicorn", "bot.api:app", "--host", "0.0.0.0", "--port", "8000"]
