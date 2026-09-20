from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional


class JobState(str, Enum):
    queued = "queued"
    preparing = "preparing"
    cutting = "cutting"
    completed = "completed"
    cancelled = "cancelled"
    failed = "failed"


@dataclass
class DeviceInfo:
    id: str
    name: str
    kind: str
    status: str = "ready"
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CutJob:
    id: str
    filename: str
    status: JobState = JobState.queued
    progress: int = 0
    device_id: Optional[str] = None
    settings: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    logs: List[str] = field(default_factory=list)
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "filename": self.filename,
            "status": self.status.value,
            "progress": self.progress,
            "device_id": self.device_id,
            "settings": self.settings,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "logs": self.logs,
            "error": self.error,
        }
