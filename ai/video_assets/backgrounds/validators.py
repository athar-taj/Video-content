from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class AssetValidator:
    """
    Validates video assets for rendering compatibility.
    """
    
    def __init__(self, min_width: int = 720, min_height: int = 1280, min_fps: int = 24):
        self.min_width = min_width
        self.min_height = min_height
        self.min_fps = min_fps

    def validate(self, metadata: Dict[str, Any]) -> bool:
        """
        Validates metadata against technical requirements.
        """
        # Check resolution
        if metadata['width'] < self.min_width or metadata['height'] < self.min_height:
            logger.warning(f"Resolution too low: {metadata['resolution']}")
            # We might still allow it if we upscale, but usually we want high quality
            
        # Check orientation (for Shorts/Reels, vertical is preferred)
        if metadata['orientation'] != "vertical":
            logger.warning(f"Video is not vertical: {metadata['resolution']}")
            
        # Check FPS
        if metadata['fps'] < self.min_fps:
            logger.warning(f"FPS too low: {metadata['fps']}")
            return False
            
        # Check duration
        if metadata['duration'] < 1.0:
            logger.warning("Video duration too short")
            return False
            
        # Supported codecs (basic list)
        supported_codecs = ['h264', 'hevc', 'av1', 'vp9']
        if metadata['codec'] not in supported_codecs:
            logger.warning(f"Unsupported codec: {metadata['codec']}")
            # FFmpeg might still handle it, but we want to be safe
            
        return True
