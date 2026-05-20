from sqlalchemy import Column, String, Float, Integer, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from db.models.base import Base

class VideoAssetModel(Base):
    __tablename__ = "video_assets"

    id = Column(String, primary_key=True)
    asset_name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    niche = Column(String)
    resolution = Column(String)
    fps = Column(Float)
    bitrate = Column(Integer)
    codec = Column(String)
    duration_seconds = Column(Float)
    aspect_ratio = Column(String)
    orientation = Column(String) # vertical, horizontal, square
    checksum = Column(String, unique=True)
    local_path = Column(String, nullable=False)
    tags = Column(JSON, default=[])
    status = Column(String, default="indexed")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    clips = relationship("VideoClipModel", back_populates="asset")
    usage_logs = relationship("AssetUsageLog", back_populates="asset")

class VideoClipModel(Base):
    __tablename__ = "video_clips"

    id = Column(String, primary_key=True)
    asset_id = Column(String, ForeignKey("video_assets.id"))
    clip_start = Column(Float)
    clip_end = Column(Float)
    output_path = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    asset = relationship("VideoAssetModel", back_populates="clips")

class AssetUsageLog(Base):
    __tablename__ = "asset_usage_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    asset_id = Column(String, ForeignKey("video_assets.id"))
    script_id = Column(Integer, ForeignKey("generated_scripts.id")) # Link to script
    render_id = Column(String) # For future rendering tracking
    usage_duration = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

    asset = relationship("VideoAssetModel", back_populates="usage_logs")

class SceneTimelineModel(Base):
    __tablename__ = "scene_timelines"

    id = Column(String, primary_key=True)
    script_id = Column(Integer, ForeignKey("generated_scripts.id"))
    narration_duration = Column(Float)
    total_scene_duration = Column(Float)
    timeline_data = Column(JSON) # Store full timeline for easy retrieval
    created_at = Column(DateTime, default=datetime.utcnow)

    segments = relationship("SceneSegmentModel", back_populates="timeline", cascade="all, delete-orphan")

class SceneSegmentModel(Base):
    __tablename__ = "scene_segments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timeline_id = Column(String, ForeignKey("scene_timelines.id"))
    asset_id = Column(String, ForeignKey("video_assets.id"))
    start_time = Column(Float)
    end_time = Column(Float)
    duration = Column(Float)
    pacing_style = Column(String)
    transition_data = Column(JSON)

    timeline = relationship("SceneTimelineModel", back_populates="segments")
