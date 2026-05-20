import logging

logger = logging.getLogger(__name__)

class AnimationRenderer:
    """Renders animated captions by generating ASS animation tags."""
    
    def get_animation_tag(self, anim_type: str) -> str:
        """Returns ASS override tags for specific animation types."""
        logger.info(f"Generating ASS tags for animation: {anim_type}")
        
        if anim_type == "fade":
            # Fade in 200ms, fade out 200ms
            return "{\\fad(200,200)}"
        elif anim_type == "pop":
            # Scale up quickly from 50% to 100%
            return "{\\t(0,150,1,\\fscx100\\fscy100)\\fscx50\\fscy50}"
        elif anim_type == "bounce":
            # Scale up to 120% then back to 100%
            return "{\\t(0,100,1,\\fscx120\\fscy120)\\t(100,200,1,\\fscx100\\fscy100)}"
        elif anim_type == "zoom":
            # Slow continuous zoom
            return "{\\t(0,2000,1,\\fscx120\\fscy120)}"
        else:
            return ""
