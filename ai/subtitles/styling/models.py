from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum

class TransitionType(str, Enum):
    FADE = "fade"
    BOUNCE = "bounce"
    POP = "pop"
    SLIDE = "slide"
    SCALE = "scale"
    SHAKE = "shake"
    PULSE = "pulse"
    ZOOM = "zoom"

class AnimationConfig(BaseModel):
    animation_name: str
    duration: float = 0.5
    transition_type: TransitionType = TransitionType.FADE
    easing: str = "linear"
    intensity: float = 1.0

class FontConfig(BaseModel):
    font_family: str = "Arial"
    font_size: int = 60
    font_weight: int = 700
    is_italic: bool = False
    is_underline: bool = False

class HighlightConfig(BaseModel):
    highlight_style: str = "active_color" # active_color, bounce, scale, glow, karaoke
    active_color: str = "&H0000FFFF" # Yellow in ASS format (AABBGGRR)
    secondary_color: str = "&H00FFFFFF" # White
    glow_color: Optional[str] = None
    scale_factor: float = 1.2

class CaptionStyle(BaseModel):
    style_name: str
    font_config: FontConfig = Field(default_factory=FontConfig)
    primary_color: str = "&H00FFFFFF" # White
    secondary_color: str = "&H0000FFFF" # Yellow
    outline_color: str = "&H00000000" # Black
    shadow_color: str = "&H00000000" # Black
    alignment: int = 2 # ASS alignment (2 = Bottom Center, 5 = Top Center, 8 = Middle Center)
    margin_x: int = 10
    margin_y: int = 10
    outline_width: int = 2
    shadow_depth: int = 0
    animation_config: Optional[AnimationConfig] = None
    highlight_config: Optional[HighlightConfig] = None
