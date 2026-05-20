import logging
from typing import Dict, Any
from sqlalchemy import select

from ai.workflows.queue.job_dispatcher import job_dispatcher
from ai.workflows.queue.job_tracker import job_tracker
from ai.workflows.queue.models import JobType, JobPriority
from db.repositories.manager import db_manager
from db.models.queue import PipelineJobModel

logger = logging.getLogger(__name__)

async def script_generation_node(state: Dict[str, Any]) -> Dict[str, Any]:
    logger.info("Executing Script Generation Node (Queue-based)...")
    
    workflow_id = state.get("job_id")
    script_data = state.get("generated_script")
    
    # 1. If script is already in state, return it immediately (idempotent resume)
    if script_data:
        logger.info("Script already present in state, skipping queue dispatch.")
        return {}

    # 2. Check if a queue job already exists for this workflow stage
    db_job_id = None
    db_status = None
    
    async with db_manager.session_factory() as session:
        stmt = select(PipelineJobModel).where(
            PipelineJobModel.workflow_id == workflow_id,
            PipelineJobModel.current_stage == JobType.SCRIPT.value
        ).order_by(PipelineJobModel.created_at.desc()).limit(1)
        result = await session.execute(stmt)
        db_job = result.scalar_one_or_none()
        if db_job:
            db_job_id = db_job.id
            db_status = db_job.status

    # 3. If job exists and is complete, fetch and return result
    if db_status == "completed" and db_job_id:
        logger.info(f"Existing script job {db_job_id} found in completed state. Resuming result.")
        result = await job_tracker.get_job_result(db_job_id)
        if result:
            return result

    # 4. If no job exists or the previous job failed, dispatch a new one
    if not db_job_id or db_status in ("failed", "dead"):
        logger.info(f"Dispatching script generation job to queue for workflow {workflow_id}...")
        
        metadata = state.get("execution_metadata", {})
        title = metadata.get("title", "")
        body = metadata.get("body", "")
        subreddit = metadata.get("subreddit", "gaming")
        topic_id = state.get("topic_id", "1")
        workflow_type = state.get("workflow_type", "cheap")
        
        payload = {
            "topic_id": topic_id,
            "title": title,
            "body": body,
            "subreddit": subreddit,
            "workflow_type": workflow_type,
            "execution_metadata": metadata
        }
        
        # Enqueue Script generation job
        db_job_id = await job_dispatcher.dispatch(
            job_type=JobType.SCRIPT,
            workflow_id=workflow_id,
            payload=payload,
            priority=JobPriority.NORMAL
        )

    # 5. Await job completion (polls database/Redis)
    logger.info(f"Awaiting completion of script job {db_job_id}...")
    result = await job_tracker.await_job_completion(db_job_id)
    return result
