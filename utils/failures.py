from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any


def write_failure_artifact(dead_letter_dir: str, payload: dict[str, Any]) -> str:
    Path(dead_letter_dir).mkdir(parents=True, exist_ok=True)
    file_path = Path(dead_letter_dir) / f"failure_{uuid.uuid4().hex}.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False, default=str)
    return str(file_path)


def write_failure_html(dead_letter_dir: str, filename: str, html: str) -> str:
    Path(dead_letter_dir).mkdir(parents=True, exist_ok=True)
    file_path = Path(dead_letter_dir) / filename
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html)
    return str(file_path)
