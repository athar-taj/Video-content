import logging
from typing import Dict, Any
from sqlalchemy import select

from ai.workflows.queue.job_dispatcher import job_dispatcher
from ai.workflows.queue.job_tracker import job_tracker
from ai.workflows.queue.models import JobType, JobPriority
from db.repositories.manager import db_manager
from db.models.queue import PipelineJobModel

logger = logging.getLogger(__name__)

async def subtitle_generation_node(state: Dict[str, Any]) -> Dict[str, Any]:
    logger.info("Executing Subtitle Generation Node (Queue-based)...")
    
    workflow_id = state.get("job_id")
    subtitle_path = state.get("subtitle_path")
    
    # 1. If subtitles already exist, return them immediately (idempotent resume)
    if subtitle_path:
        logger.info("Subtitles already present in state, skipping queue dispatch.")
        return {}

    # 2. Check if a queue job already exists for this workflow stage
    db_job_id = None
    db_status = None
    
    async with db_manager.session_factory() as session:
        stmt = select(PipelineJobModel).where(
            PipelineJobModel.workflow_id == workflow_id,
            PipelineJobModel.current_stage == JobType.SUBTITLE.value
        ).order_by(PipelineJobModel.created_at.desc()).limit(1)
        result = await session.execute(stmt)
        db_job = result.scalar_one_or_none()
        if db_job:
            db_job_id = db_job.id
            db_status = db_job.status

    # 3. If job exists and is complete, fetch and return result
    if db_status == "completed" and db_job_id:
        logger.info(f"Existing subtitle job {db_job_id} found in completed state. Resuming result.")
        result = await job_tracker.get_job_result(db_job_id)
        if result:
            return result

    # 4. If no job exists or the previous job failed, dispatch a new one
    if not db_job_id or db_status in ("failed", "dead"):
        logger.info(f"Dispatching subtitle job to queue for workflow {workflow_id}...")
        
        audio_path = state.get("narration_path")
        script_data = state.get("generated_script", {})
        
        if not audio_path:
            logger.error("No narration audio path in state for subtitles.")
            return {
                "errors": state.get("errors", []) + ["Narration audio missing for subtitle generation"]
            }
            
        payload = {
            "narration_path": audio_path,
            "generated_script": script_data,
            "script_id": state.get("execution_metadata", {}).get("script_id", 1),
            "execution_metadata": state.get("execution_metadata", {})
        }
        
        # Enqueue Subtitle job
        db_job_id = await job_dispatcher.dispatch(
            job_type=JobType.SUBTITLE,
            workflow_id=workflow_id,
            payload=payload,
            priority=JobPriority.NORMAL
        )

    # 5. Await job completion (polls database/Redis)
    logger.info(f"Awaiting completion of subtitle job {db_job_id}...")
    result = await job_tracker.await_job_completion(db_job_id)
    return result

