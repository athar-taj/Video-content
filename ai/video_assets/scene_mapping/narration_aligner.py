import logging
from typing import List
from .models import Scene

logger = logging.getLogger(__name__)

class NarrationAligner:
    """Aligns scene durations with narration timing."""
    
    def align_scene_duration(self, scenes: List[Scene], total_narration_duration: float) -> List[Scene]:
        """Align scenes to fit the total narration duration."""
        if not scenes:
            return scenes
            
        logger.info(f"Aligning {len(scenes)} scenes to narration duration: {total_narration_duration}s")
        
        # Simple proportional alignment
        total_chars = sum(len(scene.narration_text) for scene in scenes)
        
        if total_chars == 0:
            avg_duration = total_narration_duration / len(scenes)
            for scene in scenes:
                scene.duration = avg_duration
        else:
            for scene in scenes:
                # Estimate duration based on text length proportion
                proportion = len(scene.narration_text) / total_chars
                scene.duration = round(total_narration_duration * proportion, 2)
                
        # Set start and end times
        current_time = 0.0
        for scene in scenes:
            scene.start_time = round(current_time, 2)
            current_time += scene.duration
            scene.end_time = round(current_time, 2)
            
        return scenes
