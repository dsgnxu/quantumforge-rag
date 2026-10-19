from __future__ import annotations

import sys
from pathlib import Path

from fastapi import FastAPI
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.rag import ask  # noqa: E402

app = FastAPI(title="QuantumForge RAG Bot", version="1.0.0")


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1)
    top_k: int = 4
    enable_filter: bool | None = None


class AskResponse(BaseModel):
    answer: str
    sources: list[str]
    chunks_found: bool
    filtered: bool
    success: bool


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/ask", response_model=AskResponse)
def ask_endpoint(body: AskRequest) -> AskResponse:
    result = ask(
        body.question,
        top_k=body.top_k,
        enable_filter=body.enable_filter,
    )
    return AskResponse(
        answer=result.answer,
        sources=result.sources,
        chunks_found=result.chunks_found,
        filtered=result.filtered,
        success=result.success,
    )
