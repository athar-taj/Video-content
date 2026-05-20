import logging
import uuid
from typing import Dict, Any, Optional
from datetime import datetime
from rq.job import Job

from ai.workflows.queue.queue_manager import queue_manager
from ai.workflows.queue.models import JobType, JobPriority, JobStatus
from ai.workflows.queue.validators import validate_job_payload
from db.repositories.manager import db_manager
from db.models.queue import PipelineJobModel

logger = logging.getLogger(__name__)

class JobDispatcher:
    """Dispatches workflow jobs to Redis Queues and persists state in PostgreSQL."""

    @staticmethod
    def _get_queue_name(job_type: JobType) -> str:
        """Determines the queue name for a given job type."""
        return f"{job_type.value}_queue"

    async def dispatch(
        self,
        job_type: JobType,
        workflow_id: str,
        payload: Dict[str, Any],
        priority: JobPriority = JobPriority.NORMAL,
        max_retries: int = 3,
        backoff_factor: float = 2.0
    ) -> str:
        """Stages a job in the database, validates it, and dispatches it to the Redis Queue."""
        # 1. Generate unique job ID
        job_id = f"job_{uuid.uuid4().hex}"
        queue_name = self._get_queue_name(job_type)

        # 2. Validate payload
        is_valid, err_msg = validate_job_payload(job_type, payload)
        if not is_valid:
            logger.error(f"Payload validation failed for job {job_id}: {err_msg}")
            raise ValueError(f"Invalid payload: {err_msg}")

        # 3. Create database entry (Staging phase)
        async with db_manager.session_factory() as session:
            db_job = PipelineJobModel(
                id=job_id,
                workflow_id=workflow_id,
                workflow_type=payload.get("workflow_type", "cheap"),
                current_stage=job_type.value,
                queue_name=queue_name,
                priority=priority.value,
                status=JobStatus.PENDING.value,
                payload=payload,
                retry_count=0
            )
            session.add(db_job)
            await session.commit()

        # 4. Determine RQ job arguments and enqueue
        # We target a generic job handler function that will run on the workers
        # The worker module path will be e.g. "ai.workflows.workers.script_worker.process_job"
        func_path = f"ai.workflows.workers.{job_type.value}_worker.process_job"
        
        rq_queue = queue_manager.get_queue(queue_name)

        try:
            # Dispatch to Redis Queue
            # We map priority to RQ arguments if needed, or rely on queue ordering.
            # RQ supports job dependence and priority via queue name ordering (which we route via workers).
            # We pass job_id, workflow_id, payload to the execution function.
            rq_job = rq_queue.enqueue_call(
                func=func_path,
                args=(job_id, workflow_id, payload),
                job_id=job_id,
                timeout=3600,  # 1 hour timeout
                result_ttl=86400  # Keep results for 24 hours
            )
            
            logger.info(f"Enqueued {job_type.value} job {job_id} on {queue_name} (priority: {priority.value})")

            # 5. Update database status to queued
            async with db_manager.session_factory() as session:
                db_job = await session.get(PipelineJobModel, job_id)
                if db_job:
                    db_job.status = JobStatus.QUEUED.value
                    await session.commit()
            
            return job_id

        except Exception as e:
            logger.exception(f"Failed to enqueue job {job_id}: {e}")
            # Mark database entry as failed
            async with db_manager.session_factory() as session:
                db_job = await session.get(PipelineJobModel, job_id)
                if db_job:
                    db_job.status = JobStatus.FAILED.value
                    await session.commit()
            raise e

# Singleton instance
job_dispatcher = JobDispatcher()
