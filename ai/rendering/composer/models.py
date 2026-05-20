from datetime import datetime
from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, Field
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship

# --- SQLAlchemy Models ---

class Base(DeclarativeBase):
    pass

class RenderJobDB(Base):
    __tablename__ = "render_jobs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(String, unique=True, nullable=False)
    script_id = Column(String, nullable=False)
    output_path = Column(String, nullable=False)
    render_status = Column(String, default="pending")
    render_duration = Column(Float, nullable=True)
    resolution = Column(String, nullable=False, default="1080x1920")
    fps = Column(Integer, nullable=False, default=30)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    assets = relationship("RenderAssetDB", back_populates="render_job", cascade="all, delete-orphan")
    logs = relationship("RenderLogDB", back_populates="render_job", cascade="all, delete-orphan")

class RenderAssetDB(Base):
    __tablename__ = "render_assets"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    render_job_id = Column(Integer, ForeignKey("render_jobs.id"))
    asset_type = Column(String, nullable=False) # e.g., video, audio, overlay, subtitle
    asset_path = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    render_job = relationship("RenderJobDB", back_populates="assets")

class RenderLogDB(Base):
    __tablename__ = "render_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    render_job_id = Column(Integer, ForeignKey("render_jobs.id"))
    pipeline_stage = Column(String, nullable=False)
    execution_time = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    render_job = relationship("RenderJobDB", back_populates="logs")


# --- Pydantic Models for API/Logic ---

class RenderStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class OverlayConfig(BaseModel):
    overlay_path: str
    position_x: int = 0
    position_y: int = 0
    start_time: float = 0.0
    duration: Optional[float] = None
    scale_w: int = -1
    scale_h: int = -1

class FinalComposition(BaseModel):
    composition_id: str
    scenes: List[dict] = []
    overlays: List[OverlayConfig] = []
    transitions: List[dict] = []
    narration_duration: float
    total_duration: float

class RenderJob(BaseModel):
    job_id: str
    script_id: str
    narration_path: str
    subtitle_path: Optional[str] = None
    background_video_path: str
    output_path: str
    render_status: RenderStatus = RenderStatus.PENDING
    render_duration: Optional[float] = None
    resolution: str = "1080x1920"
    fps: int = 30
    created_at: datetime = Field(default_factory=datetime.utcnow)
