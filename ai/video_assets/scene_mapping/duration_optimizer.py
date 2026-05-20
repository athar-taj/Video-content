import logging
from typing import List
from .models import Scene
from .pacing_engine import PacingEngine

logger = logging.getLogger(__name__)

class DurationOptimizer:
    """Adjusts scene durations to prevent abrupt cuts and maintain pacing."""
    
    def __init__(self):
        self.pacing_engine = PacingEngine()

    def optimize_durations(self, scenes: List[Scene]) -> List[Scene]:
        """Optimize durations based on pacing constraints."""
        logger.info("Optimizing scene durations.")
        
        MIN_SAFE_DURATION = 0.5  # FFmpeg might struggle with very short clips + transitions
        
        optimized_scenes = []
        for scene in scenes:
            if scene.duration < MIN_SAFE_DURATION:
                logger.warning(f"Scene {scene.scene_id} is too short ({scene.duration}s). Stretching to {MIN_SAFE_DURATION}s.")
                scene.duration = MIN_SAFE_DURATION
                
            optimized_scenes.append(scene)
            
        # Re-adjust start/end times if we forced stretching
        current_time = 0.0
        for scene in optimized_scenes:
            scene.start_time = round(current_time, 2)
            current_time += scene.duration
            scene.end_time = round(current_time, 2)
            
        return optimized_scenes
