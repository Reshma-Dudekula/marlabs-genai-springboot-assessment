from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


def load_json_file(filename: str) -> List[Dict[str, Any]]:
    path = DATA_DIR / filename
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_policies() -> List[Dict[str, Any]]:
    return load_json_file("policies.json")


def load_callers() -> List[Dict[str, Any]]:
    return load_json_file("callers.json")
