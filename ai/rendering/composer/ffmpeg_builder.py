import logging
from typing import List, Optional
from .models import RenderJob, OverlayConfig

logger = logging.getLogger(__name__)

class FFmpegBuilder:
    """Generates FFmpeg commands and filter graphs for final rendering."""
    
    def __init__(self, ffmpeg_path: str = "ffmpeg"):
        self.ffmpeg_path = ffmpeg_path

    def build_final_render_command(
        self, 
        job: RenderJob, 
        overlays: List[OverlayConfig] = None
    ) -> List[str]:
        """Builds a comprehensive FFmpeg command for the final output."""
        logger.info(f"Building FFmpeg command for job: {job.job_id}")
        
        width, height = map(int, job.resolution.split('x'))
        overlays = overlays or []
        
        cmd = [
            self.ffmpeg_path,
            "-y"
        ]
        
        # Inputs
        # [0:v] Background Video
        cmd.extend(["-stream_loop", "-1", "-i", job.background_video_path])
        # [1:a] Narration Audio
        cmd.extend(["-i", job.narration_path])
        
        input_idx = 2
        for overlay in overlays:
            cmd.extend(["-i", overlay.overlay_path])
            input_idx += 1
            
        # Filter Complex
        filter_complex = ""
        
        # 1. Scale/Crop Background to Target Resolution
        filter_complex += f"[0:v]scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height}[bg_scaled];"
        last_v_out = "[bg_scaled]"
        
        # 2. Add Overlays
        current_overlay_idx = 2
        for i, overlay in enumerate(overlays):
            next_v_out = f"[v_out{i}]"
            # Scale overlay if needed
            scale_filter = ""
            if overlay.scale_w > 0 and overlay.scale_h > 0:
                scale_filter = f"[{current_overlay_idx}:v]scale={overlay.scale_w}:{overlay.scale_h}[ol{i}];"
                overlay_in = f"[ol{i}]"
            else:
                overlay_in = f"[{current_overlay_idx}:v]"
                
            filter_complex += scale_filter
            filter_complex += f"{last_v_out}{overlay_in}overlay={overlay.position_x}:{overlay.position_y}[v_out{i}];"
            last_v_out = next_v_out
            current_overlay_idx += 1
            
        # 3. Add Subtitles (ASS format)
        if job.subtitle_path:
            safe_sub_path = job.subtitle_path.replace('\\', '\\\\').replace(':', '\\:')
            next_v_out = "[v_with_subs]"
            filter_complex += f"{last_v_out}ass='{safe_sub_path}'{next_v_out}"
            last_v_out = next_v_out
        else:
            # Strip trailing semicolon if no subtitles were added at the end
            filter_complex = filter_complex.rstrip(";")
            
        # Add filter complex to command if it exists
        if filter_complex:
            cmd.extend(["-filter_complex", filter_complex])
            cmd.extend(["-map", last_v_out])
        else:
            cmd.extend(["-map", "0:v"])
            
        # Map audio
        cmd.extend(["-map", "1:a"])
        
        # Encoding settings
        cmd.extend([
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "23",
            "-c:a", "aac",
            "-shortest", # End when shortest stream ends (usually narration)
            job.output_path
        ])
        
        return cmd
