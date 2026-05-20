import logging
from typing import List
from .models import Scene, PacingStyle, TransitionType

logger = logging.getLogger(__name__)

class PacingEngine:
    """Controls scene speed and optimizes retention pacing."""
    
    # Define ideal duration ranges for different pacing styles
    PACING_RULES = {
        PacingStyle.SUSPENSE: {"min": 3.0, "max": 7.0, "preferred_transition": TransitionType.FADE},
        PacingStyle.DRAMATIC: {"min": 2.5, "max": 6.0, "preferred_transition": TransitionType.ZOOM},
        PacingStyle.FAST_PACED: {"min": 0.8, "max": 2.0, "preferred_transition": TransitionType.HARD_CUT},
        PacingStyle.EMOTIONAL: {"min": 3.0, "max": 5.0, "preferred_transition": TransitionType.BLUR},
        PacingStyle.CINEMATIC: {"min": 2.0, "max": 4.5, "preferred_transition": TransitionType.SLIDE},
        PacingStyle.STORYTELLING: {"min": 2.0, "max": 5.0, "preferred_transition": TransitionType.HARD_CUT},
    }

    def apply_pacing(self, scenes: List[Scene]) -> List[Scene]:
        """Apply pacing rules to scenes, assigning transitions based on pacing."""
        logger.info("Applying pacing rules to scenes.")
        for scene in scenes:
            rules = self.PACING_RULES.get(scene.pacing_style, self.PACING_RULES[PacingStyle.STORYTELLING])
            scene.transition_type = rules["preferred_transition"]
        return scenes
