import logging
from typing import Dict, Any
from sqlalchemy import select

from ai.workflows.queue.job_dispatcher import job_dispatcher
from ai.workflows.queue.job_tracker import job_tracker
from ai.workflows.queue.models import JobType, JobPriority
from db.repositories.manager import db_manager
from db.models.queue import PipelineJobModel

logger = logging.getLogger(__name__)

async def upload_node(state: Dict[str, Any]) -> Dict[str, Any]:
    logger.info("Executing Upload Node (Queue-based)...")
    
    workflow_id = state.get("job_id")
    upload_status = state.get("execution_metadata", {}).get("upload_status")
    
    # 1. If upload already completed, return immediately (idempotent resume)
    if upload_status == "success":
        logger.info("Upload already success in state, skipping queue dispatch.")
        return {}

    # 2. Check if a queue job already exists for this workflow stage
    db_job_id = None
    db_status = None
    
    async with db_manager.session_factory() as session:
        stmt = select(PipelineJobModel).where(
            PipelineJobModel.workflow_id == workflow_id,
            PipelineJobModel.current_stage == JobType.UPLOAD.value
        ).order_by(PipelineJobModel.created_at.desc()).limit(1)
        result = await session.execute(stmt)
        db_job = result.scalar_one_or_none()
        if db_job:
            db_job_id = db_job.id
            db_status = db_job.status

    # 3. If job exists and is complete, fetch and return result
    if db_status == "completed" and db_job_id:
        logger.info(f"Existing upload job {db_job_id} found in completed state. Resuming result.")
        result = await job_tracker.get_job_result(db_job_id)
        if result:
            return result

    # 4. If no job exists or previous failed, dispatch new one
    if not db_job_id or db_status in ("failed", "dead"):
        logger.info(f"Dispatching upload job to queue for workflow {workflow_id}...")
        
        render_output_path = state.get("render_output_path")
        if not render_output_path:
            logger.warning("No video to upload. Skipping upload stage.")
            return {}
            
        payload = {
            "final_video_path": render_output_path,
            "platform": "youtube_tiktok",
            "execution_metadata": state.get("execution_metadata", {})
        }
        
        # Enqueue Upload job
        db_job_id = await job_dispatcher.dispatch(
            job_type=JobType.UPLOAD,
            workflow_id=workflow_id,
            payload=payload,
            priority=JobPriority.NORMAL
        )

    # 5. Await job completion (polls database/Redis)
    logger.info(f"Awaiting completion of upload job {db_job_id}...")
    result = await job_tracker.await_job_completion(db_job_id)
    return result

