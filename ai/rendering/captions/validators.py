import logging
import os
from .models import CaptionRenderJob

logger = logging.getLogger(__name__)

class RenderValidator:
    """Validates rendering requirements and outputs."""
    
    def validate_pre_render(self, job: CaptionRenderJob) -> bool:
        """Validate assets before starting the render."""
        logger.info(f"Validating pre-render for job: {job.job_id}")
        
        if not os.path.exists(job.video_path):
            logger.error(f"Video file not found: {job.video_path}")
            return False
            
        if not os.path.exists(job.subtitle_path):
            logger.error(f"Subtitle file not found: {job.subtitle_path}")
            return False
            
        # Basic ASS validation could check if it starts with [Script Info]
        with open(job.subtitle_path, 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()
            if not first_line.startswith("[Script Info]"):
                logger.error(f"Invalid ASS syntax in {job.subtitle_path}")
                return False
                
        logger.info("Pre-render validation passed.")
        return True
        
    def validate_post_render(self, job: CaptionRenderJob) -> bool:
        """Validate output after rendering."""
        logger.info(f"Validating post-render for job: {job.job_id}")
        
        if not os.path.exists(job.output_path):
            logger.error(f"Render output not found: {job.output_path}")
            return False
            
        # Could also check file size to ensure it's not empty
        size = os.path.getsize(job.output_path)
        if size == 0:
            logger.error("Render output is 0 bytes.")
            return False
            
        logger.info("Post-render validation passed.")
        return True
