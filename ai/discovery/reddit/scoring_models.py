from pydantic import BaseModel
from typing import Dict, Any, Optional

class TrendMetrics(BaseModel):
    upvotes: int
    comments_count: int
    upvote_ratio: float = 1.0
    created_utc: float
    title: str
    body_length: int

class ScoreBreakdown(BaseModel):
    engagement: float
    recency: float
    emotional: float
    viral_total: float
    metadata: Dict[str, Any]
