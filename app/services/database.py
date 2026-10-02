from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.models import CutJob, JobState
from app.services.files import get_log_dir


class JobDatabase:
    def __init__(self, db_path: Optional[Path] = None):
        if db_path is None:
            db_path = get_log_dir() / "jobs.db"
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY,
                filename TEXT NOT NULL,
                status TEXT NOT NULL,
                progress INTEGER,
                device_id TEXT,
                settings TEXT,
                created_at TEXT,
                updated_at TEXT,
                logs TEXT,
                error TEXT
            )
        """
        )
        conn.commit()
        conn.close()

    def save_job(self, job: CutJob) -> None:
        import json

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO jobs
            (id, filename, status, progress, device_id, settings, created_at, updated_at, logs, error)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                job.id,
                job.filename,
                job.status.value,
                job.progress,
                job.device_id,
                json.dumps(job.settings),
                job.created_at,
                job.updated_at,
                json.dumps(job.logs),
                job.error,
            ),
        )
        conn.commit()
        conn.close()

    def load_job(self, job_id: str) -> Optional[CutJob]:
        import json

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
        row = cursor.fetchone()
        conn.close()

        if row is None:
            return None

        (
            job_id,
            filename,
            status,
            progress,
            device_id,
            settings,
            created_at,
            updated_at,
            logs,
            error,
        ) = row

        return CutJob(
            id=job_id,
            filename=filename,
            status=JobState(status),
            progress=progress or 0,
            device_id=device_id,
            settings=json.loads(settings) if settings else {},
            created_at=created_at,
            updated_at=updated_at,
            logs=json.loads(logs) if logs else [],
            error=error,
        )

    def list_jobs(self) -> List[CutJob]:
        import json

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM jobs ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()

        jobs = []
        for row in rows:
            (
                job_id,
                filename,
                status,
                progress,
                device_id,
                settings,
                created_at,
                updated_at,
                logs,
                error,
            ) = row
            jobs.append(
                CutJob(
                    id=job_id,
                    filename=filename,
                    status=JobState(status),
                    progress=progress or 0,
                    device_id=device_id,
                    settings=json.loads(settings) if settings else {},
                    created_at=created_at,
                    updated_at=updated_at,
                    logs=json.loads(logs) if logs else [],
                    error=error,
                )
            )
        return jobs
