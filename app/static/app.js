from __future__ import annotations

import asyncio
from typing import Any, Callable, Dict, List, Optional, Set

from app.models import CutJob, JobState
from app.services.cutter_driver import CutterDriver
from app.services.database import JobDatabase


class JobQueue:
    def __init__(self, db: Optional[JobDatabase] = None) -> None:
        self.jobs: Dict[str, CutJob] = {}
        self._tasks: Dict[str, asyncio.Task] = {}
        self._websocket_callbacks: Set[Callable[[CutJob], None]] = set()
        self.db = db or JobDatabase()
        self._load_jobs_from_db()

    def _load_jobs_from_db(self) -> None:
        for job in self.db.list_jobs():
            self.jobs[job.id] = job

    def create_job(self, filename: str, device_id: Optional[str], settings: Dict[str, Any]) -> CutJob:
        if not device_id:
            raise ValueError("A device must be selected before creating a job")

        job_num = len(self.jobs) + 1
        job = CutJob(
            id=f"job-{job_num:04d}",
            filename=filename,
            device_id=device_id,
            settings=settings,
        )
        self.jobs[job.id] = job
        self.db.save_job(job)
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
        job.logs.append("Cancellation requested")
        self.db.save_job(job)
        return job

    def start_job(
        self, job_id: str, driver: CutterDriver, on_update: Optional[Callable[[CutJob], None]] = None
    ) -> Optional[CutJob]:
        job = self.jobs.get(job_id)
        if job is None:
            return None
        if job.status in {JobState.completed, JobState.cancelled, JobState.failed}:
            return job
        if job_id in self._tasks and not self._tasks[job_id].done():
            return job
        if job.device_id is None:
            raise ValueError("A device must be selected before starting a job")

        def callback_wrapper(updated_job: CutJob) -> None:
            self.db.save_job(updated_job)
            if on_update:
                on_update(updated_job)
            for ws_callback in self._websocket_callbacks:
                try:
                    ws_callback(updated_job)
                except Exception:
                    pass

        task = asyncio.create_task(driver.run_job(job, callback_wrapper))
        self._tasks[job_id] = task
        return job

    def register_websocket_callback(self, callback: Callable[[CutJob], None]) -> None:
        self._websocket_callbacks.add(callback)

    def unregister_websocket_callback(self, callback: Callable[[CutJob], None]) -> None:
        self._websocket_callbacks.discard(callback)
