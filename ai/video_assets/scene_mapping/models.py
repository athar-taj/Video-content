from datetime import datetime
from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, Field
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import DeclarativeBase, relationship

# --- SQLAlchemy Models ---

class Base(DeclarativeBase):
    pass

class SceneTimelineDB(Base):
    __tablename__ = "scene_timelines"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    script_id = Column(String, nullable=False)
    narration_duration = Column(Float, nullable=False)
    total_scene_duration = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    segments = relationship("SceneSegmentDB", back_populates="timeline", cascade="all, delete-orphan")
    transitions = relationship("SceneTransitionDB", back_populates="timeline", cascade="all, delete-orphan")

class SceneSegmentDB(Base):
    __tablename__ = "scene_segments"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timeline_id = Column(Integer, ForeignKey("scene_timelines.id"))
    asset_id = Column(String, nullable=True)
    start_time = Column(Float, nullable=False)
    end_time = Column(Float, nullable=False)
    duration = Column(Float, nullable=False)
    pacing_style = Column(String, nullable=True)
    narration_text = Column(String, nullable=True)
    visual_style = Column(String, nullable=True)
    emotion = Column(String, nullable=True)
    
    timeline = relationship("SceneTimelineDB", back_populates="segments")

class SceneTransitionDB(Base):
    __tablename__ = "scene_transitions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timeline_id = Column(Integer, ForeignKey("scene_timelines.id"))
    transition_type = Column(String, nullable=False)
    duration = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    timeline = relationship("SceneTimelineDB", back_populates="transitions")

# --- Pydantic Models for API/Logic ---

class PacingStyle(str, Enum):
    SUSPENSE = "suspense"
    DRAMATIC = "dramatic"
    FAST_PACED = "fast-paced"
    EMOTIONAL = "emotional"
    CINEMATIC = "cinematic"
    STORYTELLING = "storytelling"

class TransitionType(str, Enum):
    FADE = "fade"
    ZOOM = "zoom"
    BLUR = "blur"
    FLASH = "flash"
    SLIDE = "slide"
    HARD_CUT = "hard-cut"

class Scene(BaseModel):
    scene_id: str
    asset_id: Optional[str] = None
    narration_text: str
    start_time: float = 0.0
    end_time: float = 0.0
    duration: float = 0.0
    visual_style: Optional[str] = "gameplay"
    transition_type: TransitionType = TransitionType.HARD_CUT
    emotion: str = "neutral"
    pacing_style: PacingStyle = PacingStyle.STORYTELLING

class SceneSegment(BaseModel):
    scene_id: str
    asset_id: str
    start_time: float
    end_time: float
    duration: float
    pacing_style: PacingStyle

class SceneTransition(BaseModel):
    from_scene: str
    to_scene: str
    transition_type: TransitionType
    duration: float

class SceneTimeline(BaseModel):
    timeline_id: str
    script_id: str
    total_duration: float
    scenes: List[Scene] = []
    transitions: List[SceneTransition] = []
    narration_duration: float
    metadata: dict = Field(default_factory=dict)
