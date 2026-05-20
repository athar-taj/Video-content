import logging
import os
from typing import Dict, Any

from ai.workflows.workers.base_worker import run_async, execute_job_wrapper
from ai.workflows.queue.models import JobType

logger = logging.getLogger(__name__)

async def _process_render_async(job_id: str, workflow_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Asynchronous business logic for compiling and rendering the video."""
    from ai.rendering.composer import FinalVideoComposer, RenderJob, ExportManager

    script_id = payload.get("script_id") or payload.get("execution_metadata", {}).get("script_id", "1")
    narration_path = payload.get("narration_path")
    subtitle_path = payload.get("subtitle_path")
    
    if not narration_path or not os.path.exists(narration_path):
        raise FileNotFoundError(f"Narration audio missing: {narration_path}")
        
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
    
    composer = FinalVideoComposer(ffmpeg_path=ffmpeg_path)
    logger.info(f"Composing video for job {job_id}...")
    
    overlays = [overlay_path] if os.path.exists(overlay_path) else []
    output = await composer.compose_video(job, overlay_paths=overlays)
    
    # Export / Archive
    try:
        export_mgr = ExportManager()
        archive_path = export_mgr.archive_render(job)
        logger.info(f"Archived video to: {archive_path}")
    except Exception as e:
        logger.warning(f"Failed to archive render: {e}")
        
    logger.info(f"Final composition complete: {output}")
    
    return {
        "render_output_path": output
    }

def process_job(job_id: str, workflow_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """RQ target function for Render Worker (processed in GPU render worker isolation)."""
    return run_async(
        execute_job_wrapper(
            job_id=job_id,
            workflow_id=workflow_id,
            payload=payload,
            job_type=JobType.RENDER,
            processor_func=_process_render_async
        )
    )
