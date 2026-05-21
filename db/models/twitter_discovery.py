from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Text, DateTime, Float, JSON, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.models.base import Base

class TwitterTrend(Base):
    __tablename__ = "twitter_trends"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    tweet_id: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    author: Mapped[str] = mapped_column(String(100), index=True)
    content: Mapped[str] = mapped_column(Text)
    hashtags: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True) # stores list of tags or stats
    
    # Engagement / Virality Metrics
    engagement_score: Mapped[float] = mapped_column(Float, default=0.0)
    viral_score: Mapped[float] = mapped_column(Float, default=0.0)
    emotional_score: Mapped[float] = mapped_column(Float, default=0.0)
    retention_score: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Workflow Metadata
    content_hash: Mapped[Optional[str]] = mapped_column(String(64), index=True)
    processing_status: Mapped[str] = mapped_column(String(50), default="fetched", index=True)
    processing_stage: Mapped[str] = mapped_column(String(50), default="discovery")
    source_type: Mapped[str] = mapped_column(String(50), default="twitter")
    language: Mapped[str] = mapped_column(String(10), default="en")
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    inserted_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class TrendCluster(Base):
    __tablename__ = "trend_clusters"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    cluster_name: Mapped[str] = mapped_column(String(255), index=True)
    cluster_score: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class InfluencerMetrics(Base):
    __tablename__ = "influencer_metrics"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    influence_score: Mapped[float] = mapped_column(Float, default=0.0)
    engagement_rate: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
