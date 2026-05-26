import logging
import asyncio
from typing import List
from .models import RenderJob, OverlayConfig
from .ffmpeg_builder import FFmpegBuilder
from .validators import CompositionValidator
from .audio_video_sync import AudioVideoSync
from .overlay_engine import OverlayEngine

logger = logging.getLogger(__name__)

class FinalVideoComposer:
    """Orchestrates the final end-to-end rendering process."""
    
    def __init__(self, ffmpeg_path: str = "ffmpeg"):
        self.ffmpeg_builder = FFmpegBuilder(ffmpeg_path)
        self.validator = CompositionValidator()
        self.av_sync = AudioVideoSync()
        self.overlay_engine = OverlayEngine()

    async def compose_video(self, job: RenderJob, overlay_paths: List[str] = None) -> str:
        """Executes the complete rendering pipeline."""
        from shared.config.settings import settings
        logger.info(f"Starting Final Video Composition for job: {job.job_id} (ENV={settings.ENV})")
        
        # 1. Validation
        if not self.validator.validate_pre_render(job):
            raise ValueError("Pre-render validation failed.")
            
        # 2. Audio/Video Sync verification
        self.av_sync.sync_durations(job)
        
        # 3. Prepare Overlays
        overlays = []
        if overlay_paths:
            overlays = self.overlay_engine.prepare_overlays(overlay_paths)
            
        # 4. Build FFmpeg Command
        cmd = self.ffmpeg_builder.build_final_render_command(job, overlays)
        
        logger.debug(f"Executing FFmpeg Command: {' '.join(cmd)}")
        
        # 5. Execute Render
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            logger.error(f"FFmpeg render failed! Error: {stderr.decode()}")
            raise RuntimeError("Final rendering failed during FFmpeg execution.")
            
        # 6. Post-render Validation
        if not self.validator.validate_post_render(job):
            raise ValueError("Post-render validation failed.")
            
        logger.info(f"Final composition successful. Output: {job.output_path}")
        return job.output_path
