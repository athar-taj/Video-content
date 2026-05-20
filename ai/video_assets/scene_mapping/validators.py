import logging
from .models import SceneTimeline

logger = logging.getLogger(__name__)

class TimelineValidator:
    """Validates scene timelines for rendering safety."""
    
    def validate(self, timeline: SceneTimeline) -> bool:
        """Check if timeline is safe for FFmpeg rendering."""
        logger.info("Validating timeline.")
        
        if not timeline.scenes:
            logger.error("Timeline has no scenes.")
            return False
            
        # Check durations
        for scene in timeline.scenes:
            if scene.duration <= 0:
                logger.error(f"Scene {scene.scene_id} has invalid duration: {scene.duration}")
                return False
                
        # Check for missing assets
        for scene in timeline.scenes:
            if not scene.asset_id:
                logger.error(f"Scene {scene.scene_id} is missing an asset.")
                return False
                
        # Check total duration vs narration (allow small floating point diff)
        diff = abs(timeline.total_duration - timeline.narration_duration)
        if diff > 1.0:
            logger.warning(f"Timeline duration ({timeline.total_duration}) mismatch with narration ({timeline.narration_duration}) by {diff}s")
            
        logger.info("Timeline validation passed.")
        return True
