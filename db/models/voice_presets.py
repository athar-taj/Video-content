from sqlalchemy import Column, String, Float, JSON, DateTime, Integer, ForeignKey
from sqlalchemy.sql import func
from db.models.base import Base

class VoicePresetModel(Base):
    __tablename__ = "voice_presets"

    id = Column(Integer, primary_key=True, index=True)
    preset_name = Column(String, unique=True, index=True, nullable=False)
    provider = Column(String, nullable=False)
    voice_name = Column(String, nullable=False)
    narration_style = Column(String)
    emotional_tone = Column(String)
    config_json = Column(JSON)  # Stores the full VoicePreset Pydantic model as JSON
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class VoiceUsageLogModel(Base):
    __tablename__ = "voice_usage_logs"

    id = Column(Integer, primary_key=True, index=True)
    preset_id = Column(String, index=True)
    script_id = Column(String, index=True, nullable=True)
    provider = Column(String)
    duration = Column(Float)
    execution_time = Column(Float)
    metadata_json = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
