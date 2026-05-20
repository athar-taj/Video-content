import logging
import os
from .models import ExecutionContext

logger = logging.getLogger(__name__)

class PipelineValidator:
    """Validates the state of the pipeline and integrity of assets."""
    
    def validate_stage_output(self, stage_name: str, context: ExecutionContext) -> bool:
        """Validates that a stage successfully produced the expected output."""
        logger.info(f"Validating output for stage: {stage_name}")
        
        if stage_name == "script":
            if not context.script_payload or "sections" not in context.script_payload:
                return False
                
        elif stage_name == "voice":
            if not context.narration_path or not os.path.exists(context.narration_path):
                return False
                
        elif stage_name == "subtitle":
            if not context.subtitle_path or not os.path.exists(context.subtitle_path):
                return False
                
        elif stage_name == "scene_mapping":
            if not context.scene_timeline:
                return False
                
        elif stage_name == "render":
            if not context.final_video_path or not os.path.exists(context.final_video_path):
                return False
                
        return True
