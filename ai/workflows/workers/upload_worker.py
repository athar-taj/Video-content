import logging
import asyncio
from typing import Dict, Any

from ai.workflows.workers.base_worker import run_async, execute_job_wrapper
from ai.workflows.queue.models import JobType

logger = logging.getLogger(__name__)

async def _process_upload_async(job_id: str, workflow_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Asynchronous business logic for uploading the video."""
    render_output_path = payload.get("final_video_path") or payload.get("render_output_path")
    if not render_output_path:
        raise ValueError("Missing 'final_video_path' or 'render_output_path' for upload job.")
        
    logger.info(f"Uploading {render_output_path} to YouTube Shorts & TikTok...")
    
    # Simulate upload API calls
    await asyncio.sleep(2.0)
    
    logger.info("Upload completed successfully!")
    
    metadata = payload.get("execution_metadata", {})
    metadata["upload_status"] = "success"
    metadata["youtube_video_id"] = "shorts_mock_12345"
    metadata["tiktok_video_id"] = "tiktok_mock_67890"
    
    return {
        "execution_metadata": metadata
    }

def process_job(job_id: str, workflow_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """RQ target function for Upload Worker."""
    return run_async(
        execute_job_wrapper(
            job_id=job_id,
            workflow_id=workflow_id,
            payload=payload,
            job_type=JobType.UPLOAD,
            processor_func=_process_upload_async
        )
    )
