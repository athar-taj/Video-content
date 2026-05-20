from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

class AssetStatus(str, Enum):
    INDEXED = "indexed"
    PROCESSING = "processing"
    ACTIVE = "active"
    ARCHIVED = "archived"
    CORRUPTED = "corrupted"
    DELETED = "deleted"

class VideoAsset(BaseModel):
    id: str
    asset_name: str
    category: str
    niche: Optional[str] = None
    source_type: str = "local"
    local_path: str
    checksum: str
    resolution: str
    fps: float
    bitrate: int
    codec: str
    duration_seconds: float
    aspect_ratio: str
    orientation: str # vertical, horizontal, square
    tags: List[str] = Field(default_factory=list)
    status: AssetStatus = AssetStatus.INDEXED
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class AssetTag(BaseModel):
    tag_name: str
    asset_id: str

class AssetCategory(BaseModel):
    name: str
    path: str
    description: Optional[str] = None

class AssetSearchResult(BaseModel):
    assets: List[VideoAsset]
    total_found: int
    query_metadata: Dict[str, Any]
