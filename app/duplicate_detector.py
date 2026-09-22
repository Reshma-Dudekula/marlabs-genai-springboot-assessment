from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Dict, List, Tuple


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def detect_duplicates(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    fingerprints: Dict[str, str] = {}
    duplicates: List[Dict[str, Any]] = []

    for item in items:
        content = item.get("content")
        if isinstance(content, str):
            payload = content.encode("utf-8")
        elif isinstance(content, (bytes, bytearray)):
            payload = bytes(content)
        else:
            payload = b""

        digest = sha256_bytes(payload)
        seen = fingerprints.get(digest)
        if seen is not None:
            item["duplicate_of"] = seen
            duplicates.append(item)
        else:
            fingerprints[digest] = item.get("filename") or item.get("document_id")
            item["duplicate_of"] = None

    return items
