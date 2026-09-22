from __future__ import annotations

import hashlib
from typing import Any, Dict, List


def is_valid_metadata(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, (str, int, float, bool)):
        return True
    if isinstance(value, list):
        return all(is_valid_metadata(item) for item in value)
    if isinstance(value, dict):
        return all(isinstance(k, str) and is_valid_metadata(v) for k, v in value.items())
    return False


def _sha256_content(value: Any) -> str:
    if isinstance(value, (bytes, bytearray)):
        raw = bytes(value)
    elif value is None:
        raw = b""
    else:
        raw = str(value).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def validate_batch_manifest(manifest: List[Dict[str, Any]]) -> Dict[str, Any]:
    errors: List[str] = []
    processed: List[Dict[str, Any]] = []
    seen_document_ids: set[str] = set()
    seen_filenames: set[str] = set()
    seen_hashes: Dict[str, str] = {}

    for index, item in enumerate(manifest):
        if not isinstance(item, dict):
            errors.append(f"Item {index}: item must be an object")
            continue
        record = dict(item)
        if "document_id" not in record:
            errors.append(f"Item {index}: missing document_id")
        elif record["document_id"] in seen_document_ids:
            errors.append(f"Item {index}: duplicate document_id")
        else:
            seen_document_ids.add(record["document_id"])

        filename = record.get("filename")
        if not filename:
            errors.append(f"Item {index}: missing file")
        elif filename in seen_filenames:
            errors.append(f"Item {index}: duplicate filename")
        else:
            seen_filenames.add(filename)

        unexpected = set(record.keys()) - {"document_id", "filename", "content", "metadata"}
        if unexpected:
            errors.append(f"Item {index}: extra file")

        metadata = record.get("metadata")
        if metadata is not None and not is_valid_metadata(metadata):
            errors.append(f"Item {index}: invalid metadata")

        content_hash = _sha256_content(record.get("content"))
        record["duplicate_of"] = seen_hashes.get(content_hash)
        if content_hash in seen_hashes:
            if not record["duplicate_of"]:
                record["duplicate_of"] = record.get("filename")
        else:
            seen_hashes[content_hash] = record.get("filename") or record.get("document_id")
        processed.append(record)

    return {"errors": errors, "items": processed}
