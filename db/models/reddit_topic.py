from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Text, DateTime, Float, JSON, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base

class RedditTopic(Base):
    __tablename__ = "reddit_topics"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    reddit_id: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    subreddit: Mapped[str] = mapped_column(String(100), index=True)
    title: Mapped[str] = mapped_column(String(500))
    body: Mapped[Optional[str]] = mapped_column(Text)
    author: Mapped[str] = mapped_column(String(100))
    score: Mapped[float] = mapped_column(Float)
    comments_count: Mapped[float] = mapped_column(Float)
    
    # Ranking Metadata
    viral_score: Mapped[float] = mapped_column(Float, default=0.0)
    engagement_score: Mapped[float] = mapped_column(Float, default=0.0)
    emotional_score: Mapped[float] = mapped_column(Float, default=0.0)
    recency_score: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Workflow Metadata
    content_hash: Mapped[Optional[str]] = mapped_column(String(64), index=True)
    processing_status: Mapped[str] = mapped_column(String(50), default="fetched", index=True)
    processing_stage: Mapped[str] = mapped_column(String(50), default="discovery")
    source_type: Mapped[str] = mapped_column(String(50), default="reddit")
    language: Mapped[str] = mapped_column(String(10), default="en")
    
    is_nsfw: Mapped[bool] = mapped_column(Boolean, default=False)
    permalink: Mapped[str] = mapped_column(String(500))
    created_utc: Mapped[datetime] = mapped_column(DateTime)
    inserted_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    comments: Mapped[List["RedditComment"]] = relationship(back_populates="topic", cascade="all, delete-orphan")
    scripts: Mapped[List["GeneratedScript"]] = relationship(back_populates="topic", cascade="all, delete-orphan")
