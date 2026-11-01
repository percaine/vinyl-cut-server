from __future__ import annotations

import os
from pathlib import Path

APP_ROOT = Path(__file__).resolve().parent.parent

UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", str(APP_ROOT / "uploads")))
LOG_DIR = Path(os.getenv("LOG_DIR", str(APP_ROOT / "logs")))
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
APP_MODE = os.getenv("APP_MODE", "prod")

# Real device backend configuration.
# Example: CUTTER_BACKEND_COMMAND="/usr/local/bin/sendto_silhouette.py"
# or: CUTTER_BACKEND_COMMAND="python3 /opt/silhouette/sendto_silhouette.py"
CUTTER_BACKEND_COMMAND = os.getenv("CUTTER_BACKEND_COMMAND")
CUTTER_BACKEND_SCRIPT = os.getenv(
    "CUTTER_BACKEND_SCRIPT",
    str(APP_ROOT / "bin" / "sendto_silhouette.py"),
)


class Settings:
    app_root = APP_ROOT
    upload_dir = UPLOAD_DIR
    log_dir = LOG_DIR
    host = HOST
    port = PORT
    app_mode = APP_MODE
    cutter_backend_command = CUTTER_BACKEND_COMMAND
    cutter_backend_script = CUTTER_BACKEND_SCRIPT


settings = Settings()
