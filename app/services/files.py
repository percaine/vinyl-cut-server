from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List


def ensure_directories() -> None:
    root = Path(__file__).resolve().parent.parent
    for folder in ["uploads", "logs"]:
        (root / folder).mkdir(exist_ok=True)


def get_root_dir() -> Path:
    return Path(__file__).resolve().parent.parent


def get_upload_dir() -> Path:
    return get_root_dir() / "uploads"


def get_log_dir() -> Path:
    return get_root_dir() / "logs"


def safe_filename(name: str) -> str:
    base = os.path.basename(name)
    safe = "".join(ch for ch in base if ch.isalnum() or ch in "._- ")
    return safe or "upload.svg"
