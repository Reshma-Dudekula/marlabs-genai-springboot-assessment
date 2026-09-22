from __future__ import annotations

import hashlib
from typing import Any, Dict, List

from app.duplicate_detector import detect_duplicates
from app.extraction import extract_document_text, extract_fields_from_text
from app.validators import validate_batch_manifest


def _compute_sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def process_batch(manifest: List[Dict[str, Any]]) -> Dict[str, Any]:
    validation = validate_batch_manifest(manifest)
    items: List[Dict[str, Any]] = []

    for item in validation["items"]:
        item_payload = dict(item)
        content = item_payload.get("content")
        filename = item_payload.get("filename")
        duplicate_of = item_payload.get("duplicate_of")

        if duplicate_of:
            item_payload["status"] = "DUPLICATE"
            item_payload["duplicate_of"] = duplicate_of
            item_payload["review_issues"] = ["Duplicate submission detected"]
            item_payload["citations"] = []
            items.append(item_payload)
            continue

        if not isinstance(content, str) or not content.strip():
            item_payload["status"] = "FAILED"
            item_payload["error_code"] = "INVALID_PAYLOAD"
            item_payload["review_issues"] = ["Missing document content"]
            items.append(item_payload)
            continue

        if filename.lower().endswith(".pdf"):
            document = extract_document_text(content.encode("latin-1", errors="replace"), filename=filename)
            if document["status"] != "OK":
                item_payload["status"] = "FAILED"
                item_payload["error_code"] = document["error_code"]
                item_payload["review_issues"] = ["PDF extraction failed"]
                items.append(item_payload)
                continue
            content = document["text"]

        extraction = extract_fields_from_text(content)
        has_evidence = any(extraction.get(field) is not None for field in ("benefit", "amount", "currency", "reference"))
        item_payload["status"] = "ANSWERED" if has_evidence and not extraction.get("review_issues") else "INSUFFICIENT_EVIDENCE"
        item_payload["benefit"] = extraction.get("benefit")
        item_payload["amount"] = extraction.get("amount")
        item_payload["currency"] = extraction.get("currency")
        item_payload["reference"] = extraction.get("reference")
        item_payload["review_required"] = True
        item_payload["review_issues"] = extraction.get("review_issues", [])
        if item_payload["status"] == "INSUFFICIENT_EVIDENCE" and not item_payload["review_issues"]:
            item_payload["review_issues"] = ["Insufficient evidence for policy evaluation"]
        item_payload["evidence"] = extraction.get("evidence", [])
        item_payload["citations"] = []
        items.append(item_payload)

    for idx, item in enumerate(items):
        if item.get("duplicate_of"):
            item["duplicate_of"] = str(item["duplicate_of"])
        if item.get("status") == "FAILED" and item.get("review_issues") is None:
            item["review_issues"] = ["Failed to extract document data"]

    return {"items": items, "errors": validation["errors"]}


def detect_duplicate_batch_items(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    for item in items:
        content = item.get("content") or ""
        digest = hashlib.sha256(str(content).encode("utf-8")).hexdigest()
        item["sha256"] = digest
    return detect_duplicates(items)
