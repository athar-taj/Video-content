from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime

class AudioStatus(str, Enum):
    PENDING = "pending"
    GENERATING = "generating"
    GENERATED = "generated"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ARCHIVED = "archived"
    FAILED = "failed"
    DELETED = "deleted"

class AudioMetadata(BaseModel):
    id: Optional[str] = None
    script_id: str
    provider: str
    voice_name: str
    preset_name: Optional[str] = None
    emotional_tone: Optional[str] = None
    narration_style: Optional[str] = None
    
    raw_audio_path: Optional[str] = None
    processed_audio_path: Optional[str] = None
    
    duration_seconds: float = 0.0
    file_size_bytes: int = 0
    checksum: Optional[str] = None
    
    sample_rate: int = 44100
    bitrate: int = 192000
    generation_time_ms: int = 0
    
    status: AudioStatus = AudioStatus.PENDING
    
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        use_enum_values = True
