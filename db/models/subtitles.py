from sqlalchemy import Column, String, Float, Integer, ForeignKey, DateTime, JSON, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base
import enum

class SubtitleStatus(enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class SubtitleGeneration(Base):
    __tablename__ = "subtitle_generations"

    id = Column(String, primary_key=True)
    script_id = Column(Integer, ForeignKey("generated_scripts.id"), nullable=True)
    audio_generation_id = Column(String, ForeignKey("audio_generations.id"), nullable=True)
    language = Column(String, default="en")
    status = Column(Enum(SubtitleStatus), default=SubtitleStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    words = relationship("WordTimestampModel", back_populates="generation", cascade="all, delete-orphan")
    segments = relationship("SubtitleSegmentModel", back_populates="generation", cascade="all, delete-orphan")
    formatted_outputs = relationship("FormattedSubtitleModel", back_populates="generation", cascade="all, delete-orphan")

class WordTimestampModel(Base):
    __tablename__ = "word_timestamps"

    id = Column(Integer, primary_key=True, autoincrement=True)
    subtitle_generation_id = Column(String, ForeignKey("subtitle_generations.id"))
    word = Column(String, nullable=False)
    start_time = Column(Float, nullable=False)
    end_time = Column(Float, nullable=False)
    confidence = Column(Float)
    position = Column(Integer)

    generation = relationship("SubtitleGeneration", back_populates="words")

class SubtitleSegmentModel(Base):
    __tablename__ = "subtitle_segments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    subtitle_generation_id = Column(String, ForeignKey("subtitle_generations.id"))
    text = Column(String, nullable=False)
    start_time = Column(Float, nullable=False)
    end_time = Column(Float, nullable=False)
    duration = Column(Float)
    word_data = Column(JSON) # Store word list as JSON for easy retrieval

    generation = relationship("SubtitleGeneration", back_populates="segments")

class FormattedSubtitleModel(Base):
    __tablename__ = "formatted_subtitles"

    id = Column(String, primary_key=True)
    subtitle_generation_id = Column(String, ForeignKey("subtitle_generations.id"))
    format = Column(String, nullable=False)
    output_path = Column(String, nullable=False)
    file_size = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    generation = relationship("SubtitleGeneration", back_populates="formatted_outputs")
    exports = relationship("SubtitleExportModel", back_populates="subtitle", cascade="all, delete-orphan")

class SubtitleExportModel(Base):
    __tablename__ = "subtitle_exports"

    id = Column(String, primary_key=True)
    subtitle_id = Column(String, ForeignKey("formatted_subtitles.id"))
    export_type = Column(String, nullable=False)
    status = Column(String, default="completed")
    created_at = Column(DateTime, default=datetime.utcnow)

    subtitle = relationship("FormattedSubtitleModel", back_populates="exports")

class CaptionStyleModel(Base):
    __tablename__ = "caption_styles"

    id = Column(String, primary_key=True)
    style_name = Column(String, nullable=False, unique=True)
    config_json = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class CaptionAnimationProfile(Base):
    __tablename__ = "caption_animation_profiles"

    id = Column(String, primary_key=True)
    animation_name = Column(String, nullable=False, unique=True)
    config_json = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class CaptionRenderProfile(Base):
    __tablename__ = "caption_render_profiles"

    id = Column(String, primary_key=True)
    profile_name = Column(String, nullable=False, unique=True)
    style_id = Column(String, ForeignKey("caption_styles.id"))
    animation_id = Column(String, ForeignKey("caption_animation_profiles.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
