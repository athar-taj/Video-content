from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class SubtitleWord(BaseModel):
    word: str
    start_time: float
    end_time: float
    confidence: float

class SubtitleSegment(BaseModel):
    segment_id: str
    text: str
    words: List[SubtitleWord]
    start_time: float
    end_time: float
    duration: float

class FormattedSubtitle(BaseModel):
    subtitle_id: str
    format: str
    output_path: str
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
