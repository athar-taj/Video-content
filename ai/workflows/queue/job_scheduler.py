import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from ai.workflows.queue.queue_manager import queue_manager
from ai.workflows.queue.models import JobType, JobPriority
from ai.workflows.queue.job_dispatcher import job_dispatcher

logger = logging.getLogger(__name__)

class JobScheduler:
    """Manages delayed jobs and scheduled batch operations."""

    async def schedule_delayed_job(
        self,
        job_type: JobType,
        workflow_id: str,
        payload: Dict[str, Any],
        delay_seconds: int,
        priority: JobPriority = JobPriority.NORMAL
    ) -> str:
        """Schedules a job to run after a specific delay (in seconds)."""
        # First, dispatch it as PENDING in PostgreSQL (staging phase)
        # We dispatch it normally but wait to put it on the queue until the delay expires,
        # OR we can enqueue it directly in Redis with a delay.
        # RQ supports scheduling natively: `queue.enqueue_in(timedelta, func, ...)`
        
        # We can register the job in DB first with status 'pending'
        from db.models.queue import PipelineJobModel
        from db.repositories.manager import db_manager
        import uuid
        
        job_id = f"job_sched_{uuid.uuid4().hex}"
        queue_name = f"{job_type.value}_queue"
        
        # Staging
        async with db_manager.session_factory() as session:
            db_job = PipelineJobModel(
                id=job_id,
                workflow_id=workflow_id,
                workflow_type=payload.get("workflow_type", "cheap"),
                current_stage=job_type.value,
                queue_name=queue_name,
                priority=priority.value,
                status="pending",
                payload=payload,
                retry_count=0
            )
            session.add(db_job)
            await session.commit()
            
        # Schedule in RQ
        rq_queue = queue_manager.get_queue(queue_name)
        func_path = f"ai.workflows.workers.{job_type.value}_worker.process_job"
        
        # Enqueue in Redis with delay
        rq_queue.enqueue_in(
            timedelta(seconds=delay_seconds),
            func_path,
            args=(job_id, workflow_id, payload),
            job_id=job_id,
            timeout=3600,
            result_ttl=86400
        )
        
        logger.info(f"Scheduled job {job_id} on {queue_name} to run in {delay_seconds}s")
        return job_id

# Singleton instance
job_scheduler = JobScheduler()
