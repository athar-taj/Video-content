from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class VideoAsset(BaseModel):
    id: str
    asset_name: str
    category: str # gameplay, cinematic, stock, etc.
    niche: Optional[str] = None # horror, relationship, motivation, etc.
    source: Optional[str] = None
    resolution: str # e.g. "1080x1920"
    fps: float
    duration_seconds: float
    file_size: int
    aspect_ratio: str # e.g. "9:16"
    tags: List[str] = Field(default_factory=list)
    local_path: str
    checksum: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class VideoClip(BaseModel):
    id: str
    asset_id: str
    clip_start: float
    clip_end: float
    output_duration: float
    processed_path: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class AssetSelection(BaseModel):
    script_id: str
    niche: str
    required_duration: float
    selected_asset_id: str
    selection_reason: str
