from __future__ import annotations

import re
from datetime import date
from typing import Any, Dict, List, Optional

from app.data_loader import load_policies
from app.extraction import extract_fields_from_text
from app.policy_engine import filter_eligible_policies


def _provider_call(*args, **kwargs):
    return {"status": "ok"}


def sanitize_answer_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    sanitized = {"benefit": None, "amount": None, "currency": None, "reference": None, "review_issues": [], "evidence": []}
    if not isinstance(payload, dict):
        return sanitized

    benefit = payload.get("benefit")
    if isinstance(benefit, str):
        cleaned = re.sub(r"<.*?>", " ", benefit)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        sanitized["benefit"] = cleaned or None

    amount_raw = payload.get("amount")
    if isinstance(amount_raw, (int, float)):
        if not re.search(r"nan|inf", str(amount_raw), flags=re.IGNORECASE):
            sanitized["amount"] = int(amount_raw)
    elif isinstance(amount_raw, str):
        match = re.search(r"-?\d+", amount_raw)
        sanitized["amount"] = int(match.group(0)) if match else None

    currency = payload.get("currency")
    if isinstance(currency, str):
        value = re.sub(r"[^A-Za-z]", "", currency).upper()
        sanitized["currency"] = value or None

    reference = payload.get("reference")
    if isinstance(reference, str):
        cleaned = re.sub(r"\s+", " ", reference).strip()
        sanitized["reference"] = cleaned or None

    issues = payload.get("review_issues") or []
    if isinstance(issues, list):
        sanitized["review_issues"] = [str(item) for item in issues if str(item).strip()]

    evidence = payload.get("evidence") or []
    if isinstance(evidence, list):
        sanitized["evidence"] = [
            {"field": str(item.get("field", "")), "value": str(item.get("value", ""))}
            for item in evidence
            if isinstance(item, dict)
        ]

    return sanitized


def _candidate_policy_values(payload: Dict[str, Any], policies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    tenant = payload.get("tenant")
    role = payload.get("role")
    as_of = payload.get("as_of") or date.today().isoformat()
    return filter_eligible_policies(policies, tenant, role, as_of)


def _policy_limit(policy: Dict[str, Any]) -> Optional[int]:
    quote = str(policy.get("quote") or "")
    match = re.search(r"(?:up to|capped at|cap(?:ped)? at|limit(?:ed)? to)\s+([\d,]+)", quote, flags=re.IGNORECASE)
    return int(match.group(1).replace(",", "")) if match else None


def answer_request(payload: Dict[str, Any]) -> Dict[str, Any]:
    try:
        _provider_call(payload)
    except TimeoutError:
        return {"result": "INSUFFICIENT_EVIDENCE", "reason": "provider timeout", "review_required": True, "review_issues": ["Provider timed out while processing request"]}
    except ConnectionError:
        return {"result": "INSUFFICIENT_EVIDENCE", "reason": "provider unavailable", "review_required": True, "review_issues": ["Provider unavailable while processing request"]}

    extraction = extract_fields_from_text(payload.get("document_text", ""))
    sanitized = sanitize_answer_payload(extraction)
    policies = load_policies()
    eligible = _candidate_policy_values(payload, policies)

    if not sanitized["benefit"] and not sanitized["amount"] and not sanitized["currency"] and not sanitized["reference"]:
        return {
            "result": "INSUFFICIENT_EVIDENCE",
            "benefit": None,
            "amount": None,
            "currency": None,
            "reference": None,
            "evidence": [],
            "review_required": True,
            "review_issues": ["Insufficient evidence for policy evaluation"],
            "citations": [],
        }

    if not eligible:
        return {
            "result": "INSUFFICIENT_EVIDENCE",
            "benefit": sanitized["benefit"],
            "amount": sanitized["amount"],
            "currency": sanitized["currency"],
            "reference": sanitized["reference"],
            "evidence": sanitized["evidence"],
            "review_required": True,
            "review_issues": ["No eligible policy found for tenant and role"],
            "citations": [],
        }

    citations = [{"chunk_id": policy.get("chunk_id"), "quote": policy.get("quote")} for policy in eligible]
    if len(eligible) > 1:
        quotes = {policy.get("quote") for policy in eligible}
        if len(quotes) > 1:
            return {
                "result": "CONFLICT",
                "benefit": sanitized["benefit"],
                "amount": sanitized["amount"],
                "currency": sanitized["currency"],
                "reference": sanitized["reference"],
                "evidence": sanitized["evidence"],
                "review_required": True,
                "review_issues": ["Conflicting eligible policies detected"],
                "citations": citations,
            }

    limit = _policy_limit(eligible[0])
    if limit is not None and sanitized["amount"] is not None and sanitized["amount"] > limit:
        return {
            "result": "INSUFFICIENT_EVIDENCE",
            "benefit": sanitized["benefit"],
            "amount": sanitized["amount"],
            "currency": sanitized["currency"],
            "reference": sanitized["reference"],
            "evidence": sanitized["evidence"],
            "review_required": True,
            "review_issues": [f"Submitted amount exceeds policy limit of {limit}"],
            "citations": citations,
        }

    return {
        "result": "ANSWERED",
        "benefit": sanitized["benefit"] or eligible[0].get("quote"),
        "amount": sanitized["amount"] if sanitized["amount"] is not None else None,
        "currency": sanitized["currency"] or "USD",
        "reference": sanitized["reference"],
        "evidence": sanitized["evidence"],
        "review_required": True,
        "review_issues": sanitized["review_issues"] + (["No issues detected"] if not sanitized["review_issues"] else []),
        "citations": citations,
    }
