from datetime import datetime
from sqlalchemy import Column, String, Integer, JSON, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from db.models.base import Base

class PipelineJobModel(Base):
    __tablename__ = "pipeline_jobs"

    id = Column(String(255), primary_key=True, index=True)  # Redis job ID
    workflow_id = Column(String(255), index=True, nullable=False)
    workflow_type = Column(String(100), nullable=False)
    current_stage = Column(String(100), nullable=False)
    queue_name = Column(String(100), nullable=False)
    priority = Column(String(50), default="normal")
    status = Column(String(50), default="pending")  # pending, queued, active, completed, failed, dead
    retry_count = Column(Integer, default=0)
    assigned_worker = Column(String(255), nullable=True)
    payload = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    failures = relationship("JobFailureModel", back_populates="job", cascade="all, delete-orphan")

class JobFailureModel(Base):
    __tablename__ = "job_failures"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String(255), ForeignKey("pipeline_jobs.id"), nullable=False)
    failure_stage = Column(String(100), nullable=False)
    error_message = Column(Text, nullable=False)
    retry_count = Column(Integer, default=0)
    worker_name = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    job = relationship("PipelineJobModel", back_populates="failures")

class WorkerStateModel(Base):
    __tablename__ = "worker_states"

    id = Column(Integer, primary_key=True, index=True)
    worker_name = Column(String(255), unique=True, index=True, nullable=False)
    queue_name = Column(String(100), nullable=False)
    status = Column(String(50), default="idle")  # idle, busy, offline
    active_jobs = Column(JSON, default=list)  # List of active job IDs
    last_heartbeat = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class DeadLetterJobModel(Base):
    __tablename__ = "dead_letter_jobs"

    id = Column(Integer, primary_key=True, index=True)
    original_job_id = Column(String(255), nullable=False)
    failure_reason = Column(Text, nullable=False)
    payload = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
