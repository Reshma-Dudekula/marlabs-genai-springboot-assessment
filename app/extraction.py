from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from PyPDF2 import PdfReader


def _normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def _sanitize_text(value: Any) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    text = re.sub(r"<script.*?>.*?</script>", "", text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"<.*?>", " ", text)
    text = text.replace("\x00", " ")
    return text.strip()


def _parse_amounts(text: str) -> List[int]:
    patterns = [
        r"(?:amount|reimbursement|coverage|claim|support|allowance)\s*[:\-]?\s*(\d[\d,]*(?:\.\d+)?)",
        r"\b\d[\d,]*(?:\.\d+)?\b",
    ]
    values: List[int] = []
    for pattern in patterns:
        matches = re.findall(pattern, text, flags=re.IGNORECASE)
        for match in matches:
            cleaned = match.replace(",", "")
            try:
                values.append(int(float(cleaned)))
            except ValueError:
                continue
        if values:
            break
    return values


def extract_fields_from_text(text: str) -> Dict[str, Any]:
    normalized = text or ""
    cleaned = _sanitize_text(normalized)
    cleaned = re.sub(r"ignore previous rules|ignore all previous instructions|system message:.*?", " ", cleaned, flags=re.IGNORECASE | re.DOTALL)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    lower_text = cleaned.lower()

    negative_phrases = [
        "no claim details", "no details provided", "no evidence", "no information",
        "no valid extractable data", "not enough information", "insufficient evidence"
    ]
    if any(phrase in lower_text for phrase in negative_phrases):
        return {
            "benefit": None,
            "amount": None,
            "currency": None,
            "reference": None,
            "review_issues": ["Insufficient evidence for policy evaluation"],
            "evidence": [],
        }

    review_issues: List[str] = []
    benefit = None
    amount = None
    currency = None
    reference = None

    benefit_labels = ["benefit", "coverage", "support", "claim", "reimbursement", "allowance"]
    benefit_match = None
    for label in benefit_labels:
        match = re.search(rf"(?:{label})\s*[:\-]?\s*([A-Za-z0-9 /&-]+?)(?=\s*(?:amount|currency|reference|claim id|claim_id|policy id|policy_id|$))", cleaned, flags=re.IGNORECASE)
        if match:
            benefit_match = match
            break
    if benefit_match:
        benefit = _normalize_text(benefit_match.group(1))

    amount_match = None
    amount_candidates = []
    for label in ["amount", "reimbursement", "coverage", "support", "allowance"]:
        match = re.search(rf"(?:{label})\s*[:\-]?\s*([^\n]+?)(?=\s*(?:currency|reference|claim id|claim_id|policy id|policy_id|benefit|coverage|support|allowance|reimbursement|$))", cleaned, flags=re.IGNORECASE)
        if match:
            amount_match = match
            value_part = match.group(1)
            amount_candidates.extend(re.findall(r"\d[\d,]*(?:\.\d+)?", value_part))
            break
    if amount_candidates:
        numeric_values = []
        for item in amount_candidates:
            cleaned_num = item.replace(",", "")
            try:
                numeric_values.append(int(float(cleaned_num)))
            except ValueError:
                continue
        if len(set(numeric_values)) > 1:
            amount = None
            review_issues.append("Conflicting amounts detected")
        elif numeric_values:
            amount = numeric_values[0]

    currency_match = re.search(r"(?:currency|currency_code)\s*[:\-]?\s*([A-Z]{3})", cleaned, flags=re.IGNORECASE)
    if currency_match:
        currency = currency_match.group(1).upper()
    elif re.search(r"\bUSD\b|\bEUR\b|\bGBP\b", cleaned, flags=re.IGNORECASE):
        currency = re.search(r"\b(USD|EUR|GBP)\b", cleaned, flags=re.IGNORECASE).group(1).upper()

    reference_match = re.search(r"(?:reference|ref|claim_id|claim id|policy_id|policy id)\s*[:\-]?\s*([A-Za-z0-9\-_/]+)", cleaned, flags=re.IGNORECASE)
    if reference_match:
        reference = reference_match.group(1)

    if not any([benefit, amount, currency, reference]):
        return {
            "benefit": None,
            "amount": None,
            "currency": None,
            "reference": None,
            "review_issues": review_issues or ["Insufficient evidence for policy evaluation"],
            "evidence": []
        }

    evidence = []
    for field, value in {"benefit": benefit, "amount": amount, "currency": currency, "reference": reference}.items():
        if value is not None:
            evidence.append({"field": field, "value": str(value)})

    return {
        "benefit": benefit,
        "amount": amount,
        "currency": currency,
        "reference": reference,
        "review_issues": review_issues,
        "evidence": evidence,
    }


def extract_document_text(file_like: Union[str, Path, bytes, bytearray], filename: Optional[str] = None) -> Dict[str, Any]:
    try:
        if isinstance(file_like, (bytes, bytearray)):
            payload = bytes(file_like)
            if not payload.startswith(b"%PDF"):
                raise ValueError("Not a PDF")
            stream = __import__("io").BytesIO(payload)
            reader = PdfReader(stream)
            pages = []
            for page in reader.pages:
                pages.append(page.extract_text() or "")
            text = "\n".join(pages)
            if not text.strip():
                raise ValueError("Empty PDF")
            return {"status": "OK", "text": text, "filename": filename or "uploaded.pdf"}

        if isinstance(file_like, (str, Path)):
            path = Path(file_like)
            if path.suffix.lower() == ".pdf":
                try:
                    reader = PdfReader(str(path))
                    pages = []
                    for page in reader.pages:
                        pages.append(page.extract_text() or "")
                    text = "\n".join(pages)
                    if not text.strip():
                        raise ValueError("Empty PDF")
                    return {"status": "OK", "text": text, "filename": path.name}
                except Exception as exc:  # noqa: BLE001
                    return {"status": "FAILED", "error_code": "PDF_EXTRACTION_FAILED", "text": "", "filename": path.name, "error": str(exc)}
            return {"status": "OK", "text": path.read_text(encoding="utf-8", errors="replace"), "filename": path.name}

        return {"status": "FAILED", "error_code": "PDF_EXTRACTION_FAILED", "text": "", "filename": filename or "unknown"}
    except Exception as exc:  # noqa: BLE001
        return {"status": "FAILED", "error_code": "PDF_EXTRACTION_FAILED", "text": "", "filename": filename or "unknown", "error": str(exc)}
