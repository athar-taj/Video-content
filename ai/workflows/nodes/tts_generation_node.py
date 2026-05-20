import logging
from typing import Dict, Any
from sqlalchemy import select

from ai.workflows.queue.job_dispatcher import job_dispatcher
from ai.workflows.queue.job_tracker import job_tracker
from ai.workflows.queue.models import JobType, JobPriority
from db.repositories.manager import db_manager
from db.models.queue import PipelineJobModel

logger = logging.getLogger(__name__)

async def tts_generation_node(state: Dict[str, Any]) -> Dict[str, Any]:
    logger.info("Executing TTS Generation Node (Queue-based)...")
    
    workflow_id = state.get("job_id")
    narration_path = state.get("narration_path")
    
    # 1. If narration audio already exists, return it immediately (idempotent resume)
    if narration_path:
        logger.info("Narration already present in state, skipping queue dispatch.")
        return {}

    # 2. Check if a queue job already exists for this workflow stage
    db_job_id = None
    db_status = None
    
    async with db_manager.session_factory() as session:
        stmt = select(PipelineJobModel).where(
            PipelineJobModel.workflow_id == workflow_id,
            PipelineJobModel.current_stage == JobType.TTS.value
        ).order_by(PipelineJobModel.created_at.desc()).limit(1)
        result = await session.execute(stmt)
        db_job = result.scalar_one_or_none()
        if db_job:
            db_job_id = db_job.id
            db_status = db_job.status

    # 3. If job exists and is complete, fetch and return result
    if db_status == "completed" and db_job_id:
        logger.info(f"Existing TTS job {db_job_id} found in completed state. Resuming result.")
        result = await job_tracker.get_job_result(db_job_id)
        if result:
            return result

    # 4. If no job exists or the previous job failed, dispatch a new one
    if not db_job_id or db_status in ("failed", "dead"):
        logger.info(f"Dispatching TTS generation job to queue for workflow {workflow_id}...")
        
        script_data = state.get("generated_script")
        if not script_data:
            logger.error("No generated script in state for TTS.")
            return {
                "errors": state.get("errors", []) + ["No script found for TTS generation"],
                "workflow_status": "failed"
            }
            
        workflow_type = state.get("workflow_type", "cheap")
        script_id = state.get("execution_metadata", {}).get("script_id", 1)
        
        payload = {
            "generated_script": script_data,
            "workflow_type": workflow_type,
            "script_id": script_id,
            "execution_metadata": state.get("execution_metadata", {})
        }
        
        # Enqueue TTS generation job
        db_job_id = await job_dispatcher.dispatch(
            job_type=JobType.TTS,
            workflow_id=workflow_id,
            payload=payload,
            priority=JobPriority.NORMAL
        )

    # 5. Await job completion (polls database/Redis)
    logger.info(f"Awaiting completion of TTS job {db_job_id}...")
    result = await job_tracker.await_job_completion(db_job_id)
    return result

