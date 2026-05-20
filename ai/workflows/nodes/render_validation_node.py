import logging
import os
from typing import Dict, Any
from ai.rendering.composer.validators import CompositionValidator
from ai.rendering.composer.models import RenderJob

logger = logging.getLogger(__name__)

async def render_validation_node(state: Dict[str, Any]) -> Dict[str, Any]:
    logger.info("Executing Render Validation Node...")
    
    render_output_path = state.get("render_output_path")
    job_id = state.get("job_id")
    script_id = state.get("execution_metadata", {}).get("script_id", "1")
    narration_path = state.get("narration_path")
    
    if not render_output_path:
        logger.error("No render output path found in state for validation.")
        return {"workflow_status": "failed", "errors": state.get("errors", []) + ["No render output to validate"]}
        
    validator = CompositionValidator()
    
    # We reconstruct a mock job for the validator
    job = RenderJob(
        job_id=job_id,
        script_id=str(script_id),
        narration_path=narration_path or "",
        background_video_path="",
        output_path=render_output_path,
        resolution="1080x1920"
    )
    
    is_valid = validator.validate_post_render(job)
    
    if is_valid:
        logger.info(f"Render output validated successfully: {render_output_path}")
        return {
            "workflow_status": "completed"
        }
    else:
        logger.error(f"Render output validation failed for: {render_output_path}")
        return {
            "workflow_status": "failed",
            "errors": state.get("errors", []) + ["Render output file is missing or empty"]
        }
