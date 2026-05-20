from typing import List, Optional
from ai.subtitles.styling.models import AnimationConfig, TransitionType

class AnimationEngine:
    """
    Generates ASS animation tags for various effects.
    """
    def __init__(self, config: Optional[AnimationConfig] = None):
        self.config = config

    def get_animation_tags(self, duration: float) -> str:
        """
        Returns ASS tags for the configured animation.
        """
        if not self.config:
            return ""
            
        fade_duration = int(self.config.duration * 1000) # ms
        
        if self.config.transition_type == TransitionType.FADE:
            return f"{{\\fad({fade_duration},{fade_duration})}}"
            
        if self.config.transition_type == TransitionType.POP:
            # Transform from 0% to 100% scale over 100ms
            return f"{{\\fscx0\\fscy0\\t(0,100,\\fscx100\\fscy100)}}"
            
        if self.config.transition_type == TransitionType.BOUNCE:
            # Simple bounce using scale and transform
            return f"{{\\fscx100\\fscy100\\t(0,100,\\fscx120\\fscy120)\\t(100,200,\\fscx100\\fscy100)}}"
            
        if self.config.transition_type == TransitionType.SHAKE:
            # Complex to do in single tag, but can use \t for positioning
            return f"{{\\t(0,50,\\pos(965,965))\\t(50,100,\\pos(960,960))}}" # Rough shake
            
        return ""

    def apply_to_text(self, text: str, segment_duration: float) -> str:
        tags = self.get_animation_tags(segment_duration)
        return f"{tags}{text}"
