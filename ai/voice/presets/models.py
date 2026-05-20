from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum

class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    NEUTRAL = "neutral"

class NarrationStyle(str, Enum):
    DEEP = "deep"
    EMOTIONAL = "emotional"
    SUSPENSE = "suspense"
    STORYTELLING = "storytelling"
    MOTIVATIONAL = "motivational"
    DRAMATIC = "dramatic"
    CALM = "calm"
    ENERGETIC = "energetic"
    MYSTERIOUS = "mysterious"

class EmotionalTone(str, Enum):
    SUSPENSE = "suspense"
    EMOTIONAL = "emotional"
    DRAMATIC = "dramatic"
    CALM = "calm"
    ENERGETIC = "energetic"
    MOTIVATIONAL = "motivational"
    MYSTERIOUS = "mysterious"
    STORYTELLING = "storytelling"

class VoicePreset(BaseModel):
    """
    Standardized model for AI Narration Voice Presets.
    Provider-agnostic and scalable for future voice cloning.
    """
    preset_name: str = Field(..., description="Unique name for the preset")
    provider: str = Field(..., description="TTS Provider name (e.g., 'sarvam', 'murf', 'kokoro')")
    voice_name: str = Field(..., description="Provider-specific voice ID or name")
    gender: Gender = Field(default=Gender.NEUTRAL)
    language: str = Field(default="en-US")
    narration_style: NarrationStyle = Field(default=NarrationStyle.STORYTELLING)
    emotional_tone: EmotionalTone = Field(default=EmotionalTone.CALM)
    
    # Prosody and Pacing controls
    speech_speed: float = Field(default=1.0, ge=0.5, le=2.0)
    pitch: float = Field(default=0.0, ge=-10.0, le=10.0)
    stability: float = Field(default=0.5, ge=0.0, le=1.0)
    energy: float = Field(default=0.5, ge=0.0, le=1.0)
    
    # Advanced Pacing
    pause_style: str = Field(default="natural", description="natural, dramatic, short")
    pacing_style: str = Field(default="steady", description="steady, dynamic, slow, fast")
    
    # Metadata for future expansion
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        use_enum_values = True
        extra = "allow"

class VoiceUsageLog(BaseModel):
    preset_id: str
    script_id: Optional[str] = None
    provider: str
    duration: float
    execution_time: float
    metadata: Dict[str, Any] = {}
