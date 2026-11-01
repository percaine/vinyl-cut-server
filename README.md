from __future__ import annotations

import asyncio
import shlex
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, List, Optional

from app.config import settings
from app.models import CutJob, JobState
from app.services.files import get_upload_dir


class CutterDriver:
    def _resolve_backend_command(self) -> Optional[List[str]]:
        if settings.cutter_backend_command:
            return shlex.split(settings.cutter_backend_command)

        script_path = Path(settings.cutter_backend_script)
        if script_path.exists() and script_path.is_file():
            return [sys.executable, str(script_path)]

        return None

    def _resolve_upload_path(self, job: CutJob) -> Path:
        candidate = (get_upload_dir() / job.filename).resolve()
        if candidate.exists():
            return candidate

        direct = Path(job.filename).expanduser().resolve()
        if direct.exists():
            return direct

        raise FileNotFoundError(f"Uploaded file not found: {job.filename}")

    def _build_backend_command(self, job: CutJob, file_path: Path) -> List[str]:
        command = self._resolve_backend_command()
        if not command:
            raise RuntimeError(
                "No real cutter backend is configured. Set CUTTER_BACKEND_COMMAND to a real Silhouette backend executable or provide a valid CUTTER_BACKEND_SCRIPT."
            )

        args = [
            str(file_path),
            "--device-id",
            str(job.device_id),
            "--speed",
            str(job.settings.get("speed", 8)),
            "--pressure",
            str(job.settings.get("pressure", 12)),
            "--tool",
            str(job.settings.get("tool", "autoblade")),
        ]

        return command + args

    def _run_backend_command(self, command: List[str]) -> str:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
        )
        output = "\n".join(part for part in [completed.stdout.strip(), completed.stderr.strip()] if part)
        if completed.returncode != 0:
            message = output or f"backend exited with code {completed.returncode}"
            raise RuntimeError(message)
        return output

    async def run_job(self, job: CutJob, update_callback: Callable[[CutJob], None]) -> None:
        try:
            job.status = JobState.preparing
            job.updated_at = datetime.now(timezone.utc).isoformat()
            job.logs.append("Preparing real cutter session")
            update_callback(job)

            if job.device_id is None:
                raise ValueError("No cutter device selected")

            file_path = self._resolve_upload_path(job)
            backend_command = self._build_backend_command(job, file_path)

            job.status = JobState.cutting
            job.updated_at = datetime.now(timezone.utc).isoformat()
            job.logs.append(f"Executing real cutter backend for device {job.device_id}")
            job.logs.append(f"Command: {' '.join(backend_command)}")
            update_callback(job)

            backend_output = await asyncio.to_thread(self._run_backend_command, backend_command)
            if backend_output:
                job.logs.append(backend_output)

            if job.status == JobState.cancelled:
                job.logs.append("Job cancelled before backend completion")
                update_callback(job)
                return

            job.status = JobState.completed
            job.progress = 100
            job.updated_at = datetime.now(timezone.utc).isoformat()
            job.logs.append("Cut completed successfully")
            update_callback(job)
        except Exception as exc:  # pragma: no cover - failure path for real device ops
            job.status = JobState.failed
            job.error = str(exc)
            job.updated_at = datetime.now(timezone.utc).isoformat()
            job.logs.append(f"Job failed: {exc}")
            update_callback(job)
        finally:
            job.updated_at = datetime.now(timezone.utc).isoformat()
