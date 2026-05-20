from sqlalchemy import String, Text, ForeignKey, Float, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from .base import Base

class RedditComment(Base):
    __tablename__ = "reddit_comments"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    topic_id: Mapped[int] = mapped_column(ForeignKey("reddit_topics.id", ondelete="CASCADE"))
    reddit_comment_id: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    comment_body: Mapped[str] = mapped_column(Text)
    score: Mapped[float] = mapped_column(Float)
    author: Mapped[str] = mapped_column(String(100))
    replies_count: Mapped[float] = mapped_column(Float, default=0)
    created_utc: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    topic: Mapped["RedditTopic"] = relationship(back_populates="comments")
