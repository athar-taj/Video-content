import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from db.repositories.manager import db_manager
from db.models.queue import DeadLetterJobModel, PipelineJobModel
from ai.workflows.queue.models import JobStatus

logger = logging.getLogger(__name__)

class DeadLetterQueue:
    """Manages permanently failed jobs (Dead Letter Queue - DLQ)."""

    async def move_to_dead_letter(self, job_id: str, error_message: str, payload: Dict[str, Any]) -> int:
        """Moves a permanently failed job to the DLQ table and updates its main status to dead."""
        async with db_manager.session_factory() as session:
            # 1. Add dead letter record
            dlq_job = DeadLetterJobModel(
                original_job_id=job_id,
                failure_reason=error_message,
                payload=payload,
                created_at=datetime.utcnow()
            )
            session.add(dlq_job)
            
            # 2. Update pipeline job status to dead
            db_job = await session.get(PipelineJobModel, job_id)
            if db_job:
                db_job.status = JobStatus.DEAD.value
                
            await session.commit()
            logger.warning(f"☠️ Job {job_id} moved to Dead Letter Queue (Reason: {error_message})")
            return dlq_job.id

    async def get_dead_jobs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieves a list of jobs currently in the Dead Letter Queue."""
        from sqlalchemy import select
        async with db_manager.session_factory() as session:
            stmt = select(DeadLetterJobModel).order_by(DeadLetterJobModel.created_at.desc()).limit(limit)
            result = await session.execute(stmt)
            jobs = result.scalars().all()
            
            return [
                {
                    "id": j.id,
                    "original_job_id": j.original_job_id,
                    "failure_reason": j.failure_reason,
                    "payload": j.payload,
                    "created_at": j.created_at.isoformat()
                }
                for j in jobs
            ]

    async def replay_job(self, dlq_id: int) -> Optional[str]:
        """Replays a job from the DLQ by re-dispatching it."""
        from ai.workflows.queue.job_dispatcher import job_dispatcher
        from ai.workflows.queue.models import JobType, JobPriority
        from sqlalchemy import delete
        
        async with db_manager.session_factory() as session:
            # Get DLQ record
            dlq_job = await session.get(DeadLetterJobModel, dlq_id)
            if not dlq_job:
                logger.error(f"DLQ job ID {dlq_id} not found.")
                return None
                
            payload = dlq_job.payload
            original_job_id = dlq_job.original_job_id
            
            # Determine type and workflow
            # Retrieve from payload
            job_type_str = payload.get("job_type", "script")
            job_type = JobType(job_type_str)
            workflow_id = payload.get("workflow_id", "manual_replay")
            priority_str = payload.get("priority", "normal")
            priority = JobPriority(priority_str)
            
            logger.info(f"Replaying DLQ Job {dlq_id} (Original ID: {original_job_id})")
            
            # Remove DLQ entry
            await session.delete(dlq_job)
            await session.commit()
            
        # Re-dispatch job (creates new run record)
        # We strip retry info from payload to reset retry counter
        clean_payload = payload.copy()
        if "retry_count" in clean_payload:
            clean_payload["retry_count"] = 0
            
        new_job_id = await job_dispatcher.dispatch(
            job_type=job_type,
            workflow_id=workflow_id,
            payload=clean_payload.get("payload", {}),
            priority=priority
        )
        return new_job_id

# Singleton instance
dead_letter_queue = DeadLetterQueue()
