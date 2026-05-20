from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum
from pydantic import BaseModel, Field
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import DeclarativeBase, relationship

# --- SQLAlchemy Models ---

class Base(DeclarativeBase):
    pass

class PipelineJobDB(Base):
    __tablename__ = "pipeline_jobs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(String, unique=True, nullable=False)
    workflow_type = Column(String, nullable=False)
    current_stage = Column(String, nullable=False)
    status = Column(String, nullable=False, default="pending")
    retry_count = Column(Integer, default=0)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    stages = relationship("PipelineStageDB", back_populates="job", cascade="all, delete-orphan")
    logs = relationship("PipelineLogDB", back_populates="job", cascade="all, delete-orphan")

class PipelineStageDB(Base):
    __tablename__ = "pipeline_stages"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    pipeline_job_id = Column(Integer, ForeignKey("pipeline_jobs.id"))
    stage_name = Column(String, nullable=False)
    status = Column(String, nullable=False)
    execution_time = Column(Integer, nullable=True) # ms
    created_at = Column(DateTime, default=datetime.utcnow)
    
    job = relationship("PipelineJobDB", back_populates="stages")

class PipelineLogDB(Base):
    __tablename__ = "pipeline_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    pipeline_job_id = Column(Integer, ForeignKey("pipeline_jobs.id"))
    log_level = Column(String, nullable=False)
    message = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    job = relationship("PipelineJobDB", back_populates="logs")

# --- Pydantic Models for API/Logic ---

class PipelineStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    ARCHIVED = "archived"

class StageStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

class PipelineState(BaseModel):
    discovery_status: StageStatus = StageStatus.PENDING
    script_status: StageStatus = StageStatus.PENDING
    voice_status: StageStatus = StageStatus.PENDING
    subtitle_status: StageStatus = StageStatus.PENDING
    scene_mapping_status: StageStatus = StageStatus.PENDING
    render_status: StageStatus = StageStatus.PENDING
    upload_status: StageStatus = StageStatus.PENDING

class PipelineJob(BaseModel):
    job_id: str
    topic_id: str
    workflow_type: str = "default_shorts"
    current_stage: str = "discovery"
    status: PipelineStatus = PipelineStatus.PENDING
    state: PipelineState = Field(default_factory=PipelineState)
    retry_count: int = 0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

class ExecutionContext(BaseModel):
    job_id: str
    topic_data: Optional[Dict[str, Any]] = None
    script_payload: Optional[Dict[str, Any]] = None
    narration_path: Optional[str] = None
    subtitle_path: Optional[str] = None
    scene_timeline: Optional[Dict[str, Any]] = None
    final_video_path: Optional[str] = None
    errors: List[str] = []
    metadata: Dict[str, Any] = {}

class PipelineContext(BaseModel):
    job_id: str
    topic_id: Optional[str] = None
    workflow_type: str = "cheap"
    viral_score: int = 0
    emotional_score: int = 0
    retention_score: int = 0
    selected_llm_provider: Optional[str] = None
    selected_tts_provider: Optional[str] = None
    generated_script: Optional[Dict[str, Any]] = None
    narration_path: Optional[str] = None
    subtitle_path: Optional[str] = None
    scene_timeline_path: Optional[str] = None
    render_output_path: Optional[str] = None
    retry_count: int = 0
    workflow_status: str = "pending"
    execution_metadata: Dict[str, Any] = Field(default_factory=dict)
    errors: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)

