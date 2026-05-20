import logging
import os
from .models import RenderJob

logger = logging.getLogger(__name__)

class CompositionValidator:
    """Validates assets and outputs for the final composition."""
    
    def validate_pre_render(self, job: RenderJob) -> bool:
        """Ensure all required assets exist before rendering."""
        logger.info(f"Validating pre-render assets for job: {job.job_id}")
        
        required_files = [job.background_video_path, job.narration_path]
        if job.subtitle_path:
            required_files.append(job.subtitle_path)
            
        for filepath in required_files:
            if not os.path.exists(filepath):
                logger.error(f"Missing required asset: {filepath}")
                return False
                
        logger.info("Pre-render validation passed.")
        return True
        
    def validate_post_render(self, job: RenderJob) -> bool:
        """Ensure the final video was created successfully."""
        logger.info(f"Validating post-render output for job: {job.job_id}")
        
        if not os.path.exists(job.output_path):
            logger.error(f"Render output missing: {job.output_path}")
            return False
            
        if os.path.getsize(job.output_path) == 0:
            logger.error("Render output is 0 bytes.")
            return False
            
        logger.info("Post-render validation passed.")
        return True
