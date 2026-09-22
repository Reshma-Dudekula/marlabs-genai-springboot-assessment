from __future__ import annotations

from typing import Dict

from fastapi import FastAPI

from app.answer_service import answer_request
from app.batch_service import process_batch
from app.models import AnswerRequest, BatchRequest

app = FastAPI(title="Marlabs Policy Assessment")


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


def _answer(payload: AnswerRequest) -> Dict[str, Any]:
    result = answer_request(payload.model_dump())
    return result


@app.post("/internal/answer")
def internal_answer_endpoint(payload: AnswerRequest) -> Dict[str, Any]:
    return _answer(payload)


@app.post("/answer")
def answer_endpoint(payload: AnswerRequest) -> Dict[str, Any]:
    return _answer(payload)


@app.post("/batches")
def batch_endpoint(payload: BatchRequest) -> Dict[str, Any]:
    manifest = [item.model_dump() for item in payload.documents]
    result = process_batch(manifest)
    if result["errors"]:
        raise HTTPException(status_code=400, detail=result["errors"])
    return result
