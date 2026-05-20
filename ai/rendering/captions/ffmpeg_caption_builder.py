import logging
from typing import List

logger = logging.getLogger(__name__)

class FFmpegCaptionBuilder:
    """Generates FFmpeg commands for caption rendering."""
    
    def __init__(self, ffmpeg_path: str = "ffmpeg"):
        self.ffmpeg_path = ffmpeg_path

    def build_ass_burn_command(self, video_path: str, subtitle_path: str, output_path: str) -> List[str]:
        """Build the FFmpeg command to burn ASS subtitles into a video."""
        logger.info(f"Building FFmpeg command for ASS burn: {subtitle_path} -> {output_path}")
        
        # Safe path formatting for FFmpeg filters
        safe_sub_path = subtitle_path.replace('\\', '\\\\').replace(':', '\\:')
        
        cmd = [
            self.ffmpeg_path,
            "-y",  # Overwrite output
            "-i", video_path,
            "-vf", f"ass='{safe_sub_path}'",
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "23",
            "-c:a", "copy",
            output_path
        ]
        return cmd
