import logging
import shutil
import os
from .models import RenderJob

logger = logging.getLogger(__name__)

class ExportManager:
    """Manages archiving and output of final renders."""
    
    def archive_render(self, job: RenderJob, archive_dir: str = "assets/renders/archive") -> str:
        """Moves a successful render to an archive directory."""
        logger.info(f"Archiving render for job: {job.job_id}")
        
        if not os.path.exists(job.output_path):
            logger.error("Output file does not exist, cannot archive.")
            return job.output_path
            
        os.makedirs(archive_dir, exist_ok=True)
        
        filename = os.path.basename(job.output_path)
        archive_path = os.path.join(archive_dir, filename)
        
        shutil.copy2(job.output_path, archive_path)
        logger.info(f"Render archived to: {archive_path}")
        
        return archive_path
