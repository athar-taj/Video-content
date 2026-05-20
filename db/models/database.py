from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Text, ForeignKey, DateTime, Float, JSON, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Topic(Base):
    __tablename__ = "topics"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    source: Mapped[str] = mapped_column(String(100), default="user")
    title: Mapped[str] = mapped_column(String(255))
    content: Mapped[Optional[str]] = mapped_column(Text)
    score: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    scripts: Mapped[List["Script"]] = relationship(back_populates="topic", cascade="all, delete-orphan")

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
    duplicate_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    ranking_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    is_nsfw: Mapped[bool] = mapped_column(Boolean, default=False)
    permalink: Mapped[str] = mapped_column(String(500))
    created_utc: Mapped[datetime] = mapped_column(DateTime)
    inserted_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    ranking_updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    comments: Mapped[List["RedditComment"]] = relationship(back_populates="topic", cascade="all, delete-orphan")

class RedditComment(Base):
    __tablename__ = "reddit_comments"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    topic_id: Mapped[int] = mapped_column(ForeignKey("reddit_topics.id"))
    comment_body: Mapped[str] = mapped_column(Text)
    score: Mapped[float] = mapped_column(Float)
    author: Mapped[str] = mapped_column(String(100))
    replies_count: Mapped[float] = mapped_column(Float, default=0)
    
    topic: Mapped["RedditTopic"] = relationship(back_populates="comments")

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
