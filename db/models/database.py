from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Text, ForeignKey, DateTime, Float, JSON, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.models.base import Base

class Topic(Base):
    __tablename__ = "topics"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    source: Mapped[str] = mapped_column(String(100), default="user")
    title: Mapped[str] = mapped_column(String(255))
    content: Mapped[Optional[str]] = mapped_column(Text)
    score: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    scripts: Mapped[List["Script"]] = relationship(back_populates="topic", cascade="all, delete-orphan")

from db.models.reddit_topic import RedditTopic
from db.models.reddit_comment import RedditComment

class Script(Base):
    __tablename__ = "scripts"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    topic_id: Mapped[int] = mapped_column(ForeignKey("topics.id"))
    hook: Mapped[str] = mapped_column(Text)
    script: Mapped[str] = mapped_column(Text)
    provider_used: Mapped[str] = mapped_column(String(50))
    quality_score: Mapped[float] = mapped_column(Float, default=0.0)
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    topic: Mapped["Topic"] = relationship(back_populates="scripts")

class WorkflowJob(Base):
    __tablename__ = "workflow_jobs"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    workflow_type: Mapped[str] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(20), default="pending")
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    errors: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    state_snapshot: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
