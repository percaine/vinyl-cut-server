from __future__ import annotations

import asyncio
from typing import Any, Dict, List, Optional

from app.models import CutJob, JobState


class JobQueue:
    def __init__(self) -> None:
        self.jobs: Dict[str, CutJob] = {}
        self._tasks: Dict[str, asyncio.Task] = {}

    def create_job(self, filename: str, device_id: Optional[str], settings: Dict[str, Any]) -> CutJob:
        job = CutJob(
            id=f"job-{len(self.jobs) + 1:04d}",
            filename=filename,
            device_id=device_id,
            settings=settings,
        )
        self.jobs[job.id] = job
        return job

    def list_jobs(self) -> List[Dict[str, Any]]:
        return [job.to_dict() for job in self.jobs.values()]

    def get_job(self, job_id: str) -> Optional[CutJob]:
        return self.jobs.get(job_id)

    def cancel_job(self, job_id: str) -> Optional[CutJob]:
        job = self.jobs.get(job_id)
        if job is None:
            return None
        if job.status in {JobState.completed, JobState.cancelled, JobState.failed}:
            return job
        job.status = JobState.cancelled
        return job

    def start_job(self, job_id: str, driver: Any, on_update: Optional[Any] = None) -> Optional[CutJob]:
        job = self.jobs.get(job_id)
        if job is None:
            return None
        if job.status in {JobState.completed, JobState.cancelled, JobState.failed}:
            return job
        if job_id in self._tasks and not self._tasks[job_id].done():
            return job
        callback = on_update or (lambda _: None)
        task = asyncio.create_task(driver.run_job(job, callback))
        self._tasks[job_id] = task
        return job
