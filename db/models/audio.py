from sqlalchemy import Column, String, Float, Integer, JSON, DateTime, Enum as SQLEnum
from sqlalchemy.sql import func
from db.models.base import Base
import enum

class AudioStatus(str, enum.Enum):
    PENDING = "pending"
    GENERATING = "generating"
    GENERATED = "generated"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ARCHIVED = "archived"
    FAILED = "failed"
    DELETED = "deleted"

class AudioGenerationModel(Base):
    __tablename__ = "audio_generations"

    id = Column(String, primary_key=True, index=True)
    script_id = Column(String, index=True, nullable=False)
    provider = Column(String, nullable=False)
    voice_name = Column(String, nullable=False)
    preset_name = Column(String)
    emotional_tone = Column(String)
    narration_style = Column(String)
    
    raw_audio_path = Column(String)
    processed_audio_path = Column(String)
    
    duration_seconds = Column(Float, default=0.0)
    file_size_bytes = Column(Integer, default=0)
    checksum = Column(String)
    
    sample_rate = Column(Integer, default=44100)
    bitrate = Column(Integer, default=192000)
    generation_time_ms = Column(Integer, default=0)
    
    status = Column(SQLEnum(AudioStatus), default=AudioStatus.PENDING)
    
    metadata_json = Column(JSON, default={})
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
