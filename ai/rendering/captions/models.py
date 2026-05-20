from datetime import datetime
from typing import Optional
from enum import Enum
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship

# --- SQLAlchemy Models ---

class Base(DeclarativeBase):
    pass

class CaptionRenderJobDB(Base):
    __tablename__ = "caption_render_jobs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    render_id = Column(String, unique=True, nullable=False)
    subtitle_path = Column(String, nullable=False)
    video_path = Column(String, nullable=False)
    output_path = Column(String, nullable=False)
    animation_profile = Column(String, nullable=True)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    animation_logs = relationship("CaptionAnimationLogDB", back_populates="render_job", cascade="all, delete-orphan")
    overlay_logs = relationship("SubtitleOverlayLogDB", back_populates="render_job", cascade="all, delete-orphan")

class CaptionAnimationLogDB(Base):
    __tablename__ = "caption_animation_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    render_job_id = Column(Integer, ForeignKey("caption_render_jobs.id"))
    animation_type = Column(String, nullable=False)
    render_duration = Column(Integer, nullable=False) # stored in ms or similar
    created_at = Column(DateTime, default=datetime.utcnow)
    
    render_job = relationship("CaptionRenderJobDB", back_populates="animation_logs")

class SubtitleOverlayLogDB(Base):
    __tablename__ = "subtitle_overlay_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    render_job_id = Column(Integer, ForeignKey("caption_render_jobs.id"))
    overlay_position = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    render_job = relationship("CaptionRenderJobDB", back_populates="overlay_logs")


# --- Pydantic Models for API/Logic ---

class AnimationProfile(str, Enum):
    HORROR = "horror"
    MOTIVATION = "motivation"
    TIKTOK_BOLD = "tiktok_bold"
    EMOTIONAL_SOFT = "emotional_soft"
    CINEMATIC_CLEAN = "cinematic_clean"
    STORYTELLING_CLASSIC = "storytelling_classic"

class RenderStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class CaptionRenderJob(BaseModel):
    job_id: str
    render_id: str
    subtitle_path: str
    video_path: str
    output_path: str
    subtitle_format: str = "ass"
    animation_profile: AnimationProfile = AnimationProfile.TIKTOK_BOLD
    render_status: RenderStatus = RenderStatus.PENDING
    created_at: datetime = datetime.utcnow()

class SubtitleOverlay(BaseModel):
    subtitle_id: str
    style_name: str
    animation_type: str
    position: str = "bottom"
    highlight_style: str = "yellow_pop"

class CaptionAnimation(BaseModel):
    animation_type: str
    duration_ms: int
    parameters: dict = {}
