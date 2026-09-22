from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field, ConfigDict
from typing import Any, Dict, List, Optional


class AnswerRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tenant: str
    role: str
    as_of: date
    document_text: str
    provider: Optional[str] = None


class BatchItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    document_id: str
    filename: str
    content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class BatchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    documents: List[BatchItem]


class AnswerResult(BaseModel):
    result: str
    benefit: Optional[str] = None
    amount: Optional[int] = None
    currency: Optional[str] = None
    reference: Optional[str] = None
    evidence: List[Dict[str, str]] = Field(default_factory=list)
    review_required: bool = True
    review_issues: List[str] = Field(default_factory=list)
    citations: List[Dict[str, str]] = Field(default_factory=list)
