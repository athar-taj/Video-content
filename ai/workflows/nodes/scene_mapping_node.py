import logging
import os
import json
from typing import Dict, Any
from ai.video_assets.scene_mapping import SceneMapper

logger = logging.getLogger(__name__)

async def scene_mapping_node(state: Dict[str, Any]) -> Dict[str, Any]:
    logger.info("Executing Scene Mapping Node...")
    
    script_id = state.get("execution_metadata", {}).get("script_id", "1")
    generated_script = state.get("generated_script", {})
    hook = generated_script.get("hook", "")
    story = generated_script.get("story", "")
    
    # Extract audio duration from metadata
    narration_duration = state.get("execution_metadata", {}).get("audio_duration", 30.0)
    
    # Build sections for SceneMapper
    script_data = {
        "sections": [
            {"type": "hook", "text": hook},
            {"type": "story", "text": story}
        ]
    }
    
    try:
        mapper = SceneMapper()
        timeline_json = await mapper.generate_timeline(
            script_id=str(script_id),
            script_data=script_data,
            narration_duration=narration_duration
        )
        
        output_dir = "assets/timelines"
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"timeline_{script_id}.json")
        
        with open(output_path, "w") as f:
            f.write(timeline_json)
            
        logger.info(f"Successfully generated visual timeline at: {output_path}")
        
        state_metadata = state.get("execution_metadata", {})
        state_metadata["timeline_json"] = json.loads(timeline_json)
        
        return {
            "scene_timeline_path": output_path,
            "execution_metadata": state_metadata
        }
        
    except Exception as e:
        logger.exception(f"Scene mapping node failed: {e}")
        return {
            "errors": state.get("errors", []) + [f"Scene mapping failed: {str(e)}"]
        }
