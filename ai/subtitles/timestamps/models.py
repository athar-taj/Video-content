from typing import List, Optional
from pydantic import BaseModel, Field

class WordTimestamp(BaseModel):
    word: str
    start_time: float
    end_time: float
    confidence: float
    position: int
    speaker: Optional[str] = None

class SubtitleSegment(BaseModel):
    segment_id: str
    text: str
    start_time: float
    end_time: float
    words: List[WordTimestamp]
    duration: float

class TranscriptAlignment(BaseModel):
    original_text: str
    transcribed_text: str
    aligned_segments: List[SubtitleSegment]
    confidence_score: float
    is_fully_aligned: bool
