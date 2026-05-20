import logging
from typing import List
from .models import Scene, SceneTransition, TransitionType

logger = logging.getLogger(__name__)

class TransitionManager:
    """Generates transitions between scenes to ensure visual continuity."""
    
    def generate_transitions(self, scenes: List[Scene]) -> List[SceneTransition]:
        """Create transition metadata between scenes."""
        logger.info("Generating scene transitions.")
        transitions = []
        
        if len(scenes) < 2:
            return transitions
            
        for i in range(len(scenes) - 1):
            current_scene = scenes[i]
            next_scene = scenes[i+1]
            
            trans_type = current_scene.transition_type
            trans_duration = 0.5  # default 0.5s transition
            
            if trans_type == TransitionType.HARD_CUT:
                trans_duration = 0.0
            
            # Ensure transition duration isn't longer than half the scene
            max_allowed = min(current_scene.duration, next_scene.duration) / 2.0
            if trans_duration > max_allowed:
                trans_duration = max_allowed
                
            if trans_duration > 0:
                transitions.append(SceneTransition(
                    from_scene=current_scene.scene_id,
                    to_scene=next_scene.scene_id,
                    transition_type=trans_type,
                    duration=round(trans_duration, 2)
                ))
                
        return transitions
