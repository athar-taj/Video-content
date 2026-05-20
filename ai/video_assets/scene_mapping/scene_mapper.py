import logging
import uuid
from typing import List, Dict, Any
from .models import Scene, PacingStyle
from .narration_aligner import NarrationAligner
from .scene_selector import SceneSelector
from .duration_optimizer import DurationOptimizer
from .pacing_engine import PacingEngine
from .transition_manager import TransitionManager
from .scene_timeline_builder import SceneTimelineBuilder
from .validators import TimelineValidator

logger = logging.getLogger(__name__)

class SceneMapper:
    """Orchestrates the translation of a script into a visual scene timeline."""
    
    def __init__(self):
        self.aligner = NarrationAligner()
        self.selector = SceneSelector()
        self.optimizer = DurationOptimizer()
        self.pacing_engine = PacingEngine()
        self.transition_manager = TransitionManager()
        self.builder = SceneTimelineBuilder()
        self.validator = TimelineValidator()

    def _detect_sections(self, script_data: Dict[str, Any]) -> List[Scene]:
        """Detect narrative sections (hook, setup, climax) and create initial scenes."""
        logger.info("Detecting script sections.")
        scenes = []
        
        sections = script_data.get("sections", [])
        
        for i, section in enumerate(sections):
            section_type = section.get("type", "storytelling")
            
            pacing = PacingStyle.STORYTELLING
            emotion = "neutral"
            
            if section_type == "hook":
                pacing = PacingStyle.FAST_PACED
                emotion = "motivation"
            elif section_type == "climax":
                pacing = PacingStyle.DRAMATIC
                emotion = "suspense"
            elif section_type == "emotional":
                pacing = PacingStyle.EMOTIONAL
                emotion = "emotional"
                
            scene = Scene(
                scene_id=f"scene_{i+1}_{uuid.uuid4().hex[:6]}",
                narration_text=section.get("text", ""),
                emotion=emotion,
                pacing_style=pacing
            )
            scenes.append(scene)
            
        return scenes

    async def generate_timeline(self, script_id: str, script_data: Dict[str, Any], narration_duration: float) -> str:
        """
        Main execution pipeline (Step 16)
        """
        logger.info(f"Starting Scene Mapping Pipeline for script {script_id}")
        
        # 1. Split Narrative Sections
        scenes = self._detect_sections(script_data)
        
        # 2. Align Narration Timing
        scenes = self.aligner.align_scene_duration(scenes, narration_duration)
        
        # 3. Apply Pacing Logic
        scenes = self.pacing_engine.apply_pacing(scenes)
        
        # 4. Optimize Durations (prevent abrupt cuts)
        scenes = self.optimizer.optimize_durations(scenes)
        
        # 5. Detect Emotion & Select Assets
        scenes = self.selector.select_assets(scenes)
        
        # 6. Apply Transitions
        transitions = self.transition_manager.generate_transitions(scenes)
        
        # 7. Generate Timeline
        timeline = self.builder.build_timeline(script_id, scenes, transitions, narration_duration)
        
        # 8. Validate Timeline
        is_valid = self.validator.validate(timeline)
        if not is_valid:
            logger.error("Timeline validation failed! Fallback required.")
            raise ValueError("Invalid timeline generated.")
            
        # 9. Export JSON
        timeline_json = self.builder.export_json(timeline)
        logger.info("Pipeline completed successfully.")
        return timeline_json
