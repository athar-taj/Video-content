import logging
from typing import Dict, Any
from sqlalchemy import select

from ai.workflows.queue.job_dispatcher import job_dispatcher
from ai.workflows.queue.job_tracker import job_tracker
from ai.workflows.queue.models import JobType, JobPriority
from db.repositories.manager import db_manager
from db.models.queue import PipelineJobModel

logger = logging.getLogger(__name__)

async def analytics_feedback_node(state: Dict[str, Any]) -> Dict[str, Any]:
    logger.info("Executing Analytics Feedback Node (Queue-based)...")
    
    workflow_id = state.get("job_id")
    
    # 1. Check if a queue job already exists for this workflow stage
    db_job_id = None
    db_status = None
    
    async with db_manager.session_factory() as session:
        stmt = select(PipelineJobModel).where(
            PipelineJobModel.workflow_id == workflow_id,
            PipelineJobModel.current_stage == JobType.ANALYTICS.value
        ).order_by(PipelineJobModel.created_at.desc()).limit(1)
        result = await session.execute(stmt)
        db_job = result.scalar_one_or_none()
        if db_job:
            db_job_id = db_job.id
            db_status = db_job.status

    # 2. If job exists and is complete, return success immediately
    if db_status == "completed" and db_job_id:
        logger.info(f"Existing analytics job {db_job_id} found in completed state. Resuming.")
        return {}

    # 3. If no job exists or previous failed, dispatch a new one
    if not db_job_id or db_status in ("failed", "dead"):
        logger.info(f"Dispatching analytics job to queue for workflow {workflow_id}...")
        
        script_data = state.get("generated_script", {})
        payload = {
            "video_id": f"vid_{workflow_id}",
            "platform": "youtube_shorts",
            "generated_script": script_data,
            "selected_llm_provider": state.get("selected_llm_provider", "Unknown"),
            "selected_tts_provider": state.get("selected_tts_provider", "Unknown"),
            "workflow_type": state.get("workflow_type", "cheap"),
            "execution_metadata": state.get("execution_metadata", {})
        }
        
        # Enqueue Analytics job
        db_job_id = await job_dispatcher.dispatch(
            job_type=JobType.ANALYTICS,
            workflow_id=workflow_id,
            payload=payload,
            priority=JobPriority.LOW
        )

    # 4. Await job completion (polls database/Redis)
    logger.info(f"Awaiting completion of analytics job {db_job_id}...")
    await job_tracker.await_job_completion(db_job_id)
    return {}

