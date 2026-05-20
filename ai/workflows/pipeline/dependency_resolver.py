import logging
from typing import Dict, Any
from .models import ExecutionContext

logger = logging.getLogger(__name__)

class DependencyResolver:
    """Verifies stage prerequisites and required assets."""
    
    def check_prerequisites(self, stage_name: str, context: ExecutionContext) -> bool:
        """Ensure all required data exists in context for the given stage."""
        logger.debug(f"Resolving dependencies for stage: {stage_name}")
        
        if stage_name == "script":
            if not context.topic_data:
                logger.error("Script stage requires topic_data.")
                return False
                
        elif stage_name == "voice":
            if not context.script_payload:
                logger.error("Voice stage requires script_payload.")
                return False
                
        elif stage_name == "subtitle":
            if not context.script_payload or not context.narration_path:
                logger.error("Subtitle stage requires script_payload and narration_path.")
                return False
                
        elif stage_name == "scene_mapping":
            if not context.script_payload:
                logger.error("Scene mapping stage requires script_payload.")
                return False
                
        elif stage_name == "render":
            if not context.scene_timeline or not context.narration_path:
                logger.error("Render stage requires scene_timeline and narration_path.")
                return False
                
        return True
