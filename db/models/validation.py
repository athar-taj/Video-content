from typing import Optional
from sqlalchemy import String, Text, ForeignKey, DateTime, Float, JSON, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from .base import Base

class ScriptValidation(Base):
    __tablename__ = "script_validations"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    script_id: Mapped[int] = mapped_column(ForeignKey("generated_scripts.id", ondelete="CASCADE"), index=True)
    
    passed: Mapped[bool] = mapped_column(Boolean, default=False)
    quality_score: Mapped[float] = mapped_column(Float, default=0.0)
    profanity_score: Mapped[float] = mapped_column(Float, default=0.0)
    duplicate_score: Mapped[float] = mapped_column(Float, default=0.0)
    readability_score: Mapped[float] = mapped_column(Float, default=0.0)
    
    failures_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    duration_estimate: Mapped[float] = mapped_column(Float, default=0.0)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
