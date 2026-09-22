from __future__ import annotations

from datetime import date
from typing import Any, Dict, Iterable, List


def _coerce_date(value: Any) -> date:
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        return date.fromisoformat(value)
    raise TypeError(f"Unsupported date value: {value!r}")


def filter_eligible_policies(policies: Iterable[Dict[str, Any]], tenant: str, role: str, as_of: date | str) -> List[Dict[str, Any]]:
    as_of_date = _coerce_date(as_of)
    eligible: List[Dict[str, Any]] = []

    for policy in policies:
        if not isinstance(policy, dict):
            continue
        if policy.get("status") != "Approved":
            continue
        if policy.get("tenant") != tenant:
            continue
        if policy.get("role") != role:
            continue

        effective_from = _coerce_date(policy.get("effective_from"))
        effective_to = _coerce_date(policy.get("effective_to"))
        if effective_from <= as_of_date and effective_to > as_of_date:
            eligible.append(policy)

    return eligible


def evaluate_policy_conflict(policies: Iterable[Dict[str, Any]], tenant: str, role: str, as_of: date | str) -> bool:
    eligible = filter_eligible_policies(policies, tenant, role, as_of)
    if len(eligible) <= 1:
        return False

    unique_values = {policy.get("quote") for policy in eligible}
    return len(unique_values) > 1
