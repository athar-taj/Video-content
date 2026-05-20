import logging
import asyncio
import os
from .models import CaptionRenderJob, AnimationProfile
from .ass_renderer import ASSRenderer
from .animation_renderer import AnimationRenderer
from .karaoke_renderer import KaraokeRenderer
from .subtitle_overlay_engine import SubtitleOverlayEngine
from .ffmpeg_caption_builder import FFmpegCaptionBuilder
from .validators import RenderValidator

logger = logging.getLogger(__name__)

class CaptionBurner:
    """Orchestrates the subtitle rendering and burning process."""
    
    def __init__(self, ffmpeg_path: str = "ffmpeg"):
        self.ass_renderer = ASSRenderer()
        self.animation_renderer = AnimationRenderer()
        self.karaoke_renderer = KaraokeRenderer()
        self.overlay_engine = SubtitleOverlayEngine()
        self.ffmpeg_builder = FFmpegCaptionBuilder(ffmpeg_path)
        self.validator = RenderValidator()

    def generate_ass_file(self, job: CaptionRenderJob, dialogue_lines: list, animation_type: str = "fade", position: str = "safe_mobile") -> str:
        """Generates the actual .ass file on disk with the requested styles and animations."""
        logger.info(f"Generating ASS file for job: {job.job_id}")
        
        anim_tag = self.animation_renderer.get_animation_tag(animation_type)
        pos_tag = self.overlay_engine.get_margin_overrides(position)
        
        # Apply tags to lines
        processed_lines = []
        for line in dialogue_lines:
            words = line.get("words")
            if words:
                text = self.karaoke_renderer.generate_karaoke_line(words)
            else:
                text = line.get("text", "")
                
            effect = f"{pos_tag}{anim_tag}"
            processed_lines.append({
                "start": line.get("start"),
                "end": line.get("end"),
                "text": text,
                "effect": effect
            })
            
        ass_content = self.ass_renderer.generate_ass_content(processed_lines, profile=job.animation_profile.value)
        
        with open(job.subtitle_path, 'w', encoding='utf-8') as f:
            f.write(ass_content)
            
        return job.subtitle_path

    async def burn_subtitles(self, job: CaptionRenderJob) -> str:
        """Execute the FFmpeg command to burn subtitles into the video."""
        logger.info(f"Starting subtitle burn for job: {job.job_id}")
        
        if not self.validator.validate_pre_render(job):
            raise ValueError("Pre-render validation failed.")
            
        cmd = self.ffmpeg_builder.build_ass_burn_command(
            video_path=job.video_path,
            subtitle_path=job.subtitle_path,
            output_path=job.output_path
        )
        
        logger.debug(f"Executing FFmpeg command: {' '.join(cmd)}")
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            logger.error(f"FFmpeg render failed! Error: {stderr.decode()}")
            raise RuntimeError("Subtitle rendering failed during FFmpeg execution.")
            
        if not self.validator.validate_post_render(job):
            raise ValueError("Post-render validation failed.")
            
        logger.info(f"Caption burn completed successfully. Output: {job.output_path}")
        return job.output_path
