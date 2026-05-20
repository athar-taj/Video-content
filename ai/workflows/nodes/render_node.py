import logging
import os
from typing import Dict, Any
from ai.rendering.composer import FinalVideoComposer, RenderJob, ExportManager

logger = logging.getLogger(__name__)

async def render_node(state: Dict[str, Any]) -> Dict[str, Any]:
    logger.info("Executing Render Node...")
    
    job_id = state.get("job_id")
    script_id = state.get("execution_metadata", {}).get("script_id", "1")
    narration_path = state.get("narration_path")
    subtitle_path = state.get("subtitle_path")
    
    if not narration_path or not os.path.exists(narration_path):
        logger.error(f"Narration audio missing: {narration_path}")
        return {"errors": state.get("errors", []) + ["Narration audio missing for rendering"]}
        
    ffmpeg_path = "C:\\Users\\athar\\AppData\\Local\\Microsoft\\WinGet\\Packages\\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\\ffmpeg-8.1.1-full_build\\bin\\ffmpeg.exe"
    if not os.path.exists(ffmpeg_path):
        ffmpeg_path = "ffmpeg" # fallback to path
        
    video_path = os.path.join("assets", "input", "video", "gameplay_test.mp4")
    overlay_path = os.path.join("assets", "input", "video", "watermark.png")
    final_output_path = os.path.join("assets", "renders", f"render_{job_id}.mp4")
    
    os.makedirs(os.path.dirname(final_output_path), exist_ok=True)
    
    # Construct Render Job
    job = RenderJob(
        job_id=job_id,
        script_id=str(script_id),
        narration_path=narration_path,
        background_video_path=video_path,
        subtitle_path=subtitle_path if subtitle_path and os.path.exists(subtitle_path) else None,
        output_path=final_output_path,
        resolution="1080x1920"
    )
    
    try:
        composer = FinalVideoComposer(ffmpeg_path=ffmpeg_path)
        logger.info(f"Composing video for job {job_id}...")
        
        overlays = [overlay_path] if os.path.exists(overlay_path) else []
        output = await composer.compose_video(job, overlay_paths=overlays)
        
        # Export / Archive
        export_mgr = ExportManager()
        archive_path = export_mgr.archive_render(job)
        
        logger.info(f"Final composition complete: {output}")
        
        return {
            "render_output_path": output
        }
        
    except Exception as e:
        logger.exception(f"Render node failed: {e}")
        return {
            "errors": state.get("errors", []) + [f"Render execution failed: {str(e)}"]
        }
