from typing import Optional
from sqlalchemy import String, Text, ForeignKey, DateTime, Float, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from .base import Base

class GeneratedScript(Base):
    __tablename__ = "generated_scripts"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    topic_id: Mapped[int] = mapped_column(ForeignKey("reddit_topics.id", ondelete="CASCADE"))
    
    hook: Mapped[str] = mapped_column(Text)
    full_script: Mapped[str] = mapped_column(Text)
    
    duration_target: Mapped[int] = mapped_column(Float)
    estimated_duration: Mapped[float] = mapped_column(Float)
    
    provider_used: Mapped[str] = mapped_column(String(100))
    hook_type: Mapped[Optional[str]] = mapped_column(String(50))
    
    quality_score: Mapped[float] = mapped_column(Float, default=0.0)
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    topic: Mapped["RedditTopic"] = relationship(back_populates="scripts")

# Update RedditTopic backref in reddit_topic.py will be needed
