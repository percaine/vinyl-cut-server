from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional

from app.models import CutJob, JobState


class CutterDriver:
    async def run_job(self, job: CutJob, update_callback: Callable[[CutJob], None]) -> None:
        try:
            job.status = JobState.preparing
            job.updated_at = datetime.now(timezone.utc).isoformat()
            job.logs.append("Preparing cutter session")
            update_callback(job)
            await asyncio.sleep(1)

            if job.device_id is None:
                raise ValueError("No cutter device selected")

            job.status = JobState.cutting
            job.updated_at = datetime.now(timezone.utc).isoformat()
            job.logs.append(f"Starting cut on device {job.device_id}")
            update_callback(job)

            for percent in range(5, 101, 5):
                if job.status == JobState.cancelled:
                    job.logs.append("Job cancelled by user")
                    update_callback(job)
                    return
                job.progress = percent
                job.updated_at = datetime.now(timezone.utc).isoformat()
                job.logs.append(f"Cut progress: {percent}%")
                update_callback(job)
                await asyncio.sleep(0.5)

            if job.status == JobState.cancelled:
                return

            job.status = JobState.completed
            job.progress = 100
            job.updated_at = datetime.now(timezone.utc).isoformat()
            job.logs.append("Cut completed successfully")
            update_callback(job)
        except Exception as exc:  # pragma: no cover - failure path for device ops
            job.status = JobState.failed
            job.error = str(exc)
            job.updated_at = datetime.now(timezone.utc).isoformat()
            job.logs.append(f"Job failed: {exc}")
            update_callback(job)
        finally:
            job.updated_at = datetime.now(timezone.utc).isoformat()
