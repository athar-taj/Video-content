from datetime import datetime
from typing import Dict, Any, Optional, List
from enum import Enum
from pydantic import BaseModel, Field

class JobPriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    PREMIUM = "premium"
    URGENT = "urgent"

class JobStatus(str, Enum):
    PENDING = "pending"
    QUEUED = "queued"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    DEAD = "dead"

class WorkerStatus(str, Enum):
    IDLE = "idle"
    BUSY = "busy"
    OFFLINE = "offline"

class JobType(str, Enum):
    SCRIPT = "script"
    TTS = "tts"
    SUBTITLE = "subtitle"
    RENDER = "render"
    UPLOAD = "upload"
    ANALYTICS = "analytics"

class JobPayload(BaseModel):
    job_id: str
    workflow_id: str
    job_type: JobType
    priority: JobPriority = JobPriority.NORMAL
    payload: Dict[str, Any] = Field(default_factory=dict)
    retry_count: int = 0
    max_retries: int = 3
    backoff_factor: float = 2.0
    created_at: datetime = Field(default_factory=datetime.utcnow)

class WorkerState(BaseModel):
    worker_name: str
    queue_name: str
    status: WorkerStatus = WorkerStatus.IDLE
    active_jobs: List[str] = Field(default_factory=list)
    last_heartbeat: datetime = Field(default_factory=datetime.utcnow)

class JobFailure(BaseModel):
    job_id: str
    failure_stage: str
    error_message: str
    retry_count: int
    worker_name: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class DeadLetterJob(BaseModel):
    original_job_id: str
    failure_reason: str
    payload: Dict[str, Any]
    created_at: datetime = Field(default_factory=datetime.utcnow)
