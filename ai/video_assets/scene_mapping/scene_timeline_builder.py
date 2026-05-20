import logging
import json
from typing import List
from .models import Scene, SceneTransition, SceneTimeline

logger = logging.getLogger(__name__)

class SceneTimelineBuilder:
    """Builds the final render-ready timeline JSON."""
    
    def build_timeline(self, script_id: str, scenes: List[Scene], transitions: List[SceneTransition], narration_duration: float) -> SceneTimeline:
        """Construct the SceneTimeline object."""
        logger.info(f"Building timeline for script {script_id}")
        
        total_duration = sum(scene.duration for scene in scenes)
        
        timeline = SceneTimeline(
            timeline_id=f"tl_{script_id}",
            script_id=script_id,
            total_duration=round(total_duration, 2),
            scenes=scenes,
            transitions=transitions,
            narration_duration=round(narration_duration, 2)
        )
        return timeline
        
    def export_json(self, timeline: SceneTimeline) -> str:
        """Export timeline to a renderer-compatible JSON string."""
        
        # Format as requested in Step 13
        export_data = {
            "timeline": []
        }
        
        # Create a map of from_scene to transition
        trans_map = {t.from_scene: t for t in timeline.transitions}
        
        for scene in timeline.scenes:
            trans = trans_map.get(scene.scene_id)
            export_data["timeline"].append({
                "scene_id": scene.scene_id,
                "asset": scene.asset_id,
                "start": scene.start_time,
                "end": scene.end_time,
                "transition": trans.transition_type.value if trans else "none",
                "transition_duration": trans.duration if trans else 0.0,
                "emotion": scene.emotion
            })
            
        return json.dumps(export_data, indent=2)
