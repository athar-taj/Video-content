from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class AssetValidator:
    """
    Validates assets for rendering safety and technical quality.
    """
    
    @staticmethod
    def validate(metadata: Dict[str, Any]) -> bool:
        """
        Validates metadata for corrupted files, unsupported codecs, low resolution, etc.
        """
        # 1. Corrupted/Empty
        if metadata['duration_seconds'] <= 0 or metadata['file_size'] <= 0:
            logger.error("Asset is corrupted or empty")
            return False
            
        # 2. Resolution (Example: Min 720p)
        if metadata['width'] < 720 and metadata['height'] < 720:
            logger.warning(f"Resolution might be too low: {metadata['resolution']}")
            
        # 3. FPS
        if metadata['fps'] < 20:
            logger.error(f"Invalid or low FPS: {metadata['fps']}")
            return False
            
        # 4. Codecs (Standard web/rendering compatible)
        supported_codecs = ['h264', 'hevc', 'av1', 'vp9', 'prores', 'mpeg4']
        if metadata['codec'] not in supported_codecs:
            logger.warning(f"Unsupported or unusual codec: {metadata['codec']}")
            
        return True
