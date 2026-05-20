import logging
import asyncio
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, Any, Callable, Awaitable

from db.repositories.manager import db_manager
from db.models.queue import PipelineJobModel, JobFailureModel
from ai.workflows.queue.models import JobStatus, JobType
from ai.workflows.queue.retry_manager import retry_manager
from ai.workflows.queue.dead_letter_queue import dead_letter_queue
from ai.workflows.queue.queue_manager import queue_manager

logger = logging.getLogger(__name__)

def run_async(coro: Awaitable) -> Any:
    """Helper to run async coroutines in a synchronous worker thread."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)

async def execute_job_wrapper(
    job_id: str,
    workflow_id: str,
    payload: Dict[str, Any],
    job_type: JobType,
    processor_func: Callable[[str, str, Dict[str, Any]], Awaitable[Dict[str, Any]]],
    max_retries: int = 3,
    base_delay: float = 2.0
) -> Dict[str, Any]:
    """Base execution wrapper for all background workers.
    Handles DB logging, state transitions, retries with backoff, and DLQ.
    """
    worker_name = os.environ.get("WORKER_NAME", f"worker_{os.getpid()}")
    logger.info(f"Worker {worker_name} processing {job_type.value} job {job_id}")

    # 1. Update job to ACTIVE
    async with db_manager.session_factory() as session:
        db_job = await session.get(PipelineJobModel, job_id)
        if db_job:
            db_job.status = JobStatus.ACTIVE.value
            db_job.assigned_worker = worker_name
            db_job.updated_at = datetime.utcnow()
            await session.commit()
        else:
            logger.error(f"Job {job_id} not found in PostgreSQL database during execution start.")

    # 2. Run processor function
    try:
        # Business logic executed here
        result = await processor_func(job_id, workflow_id, payload)
        
        # 3. Handle success
        async with db_manager.session_factory() as session:
            db_job = await session.get(PipelineJobModel, job_id)
            if db_job:
                db_job.status = JobStatus.COMPLETED.value
                # Keep payload and add result field
                payload_updated = db_job.payload or {}
                payload_updated["result"] = result
                db_job.payload = payload_updated
                db_job.updated_at = datetime.utcnow()
                await session.commit()
                
        logger.info(f"✅ Job {job_id} completed successfully.")
        return result

    except Exception as e:
        error_msg = f"{type(e).__name__}: {str(e)}"
        logger.exception(f"❌ Error processing job {job_id}: {error_msg}")

        # Fetch current retry count
        async with db_manager.session_factory() as session:
            db_job = await session.get(PipelineJobModel, job_id)
            current_retry = db_job.retry_count if db_job else 0
            
            # Log failure details in database
            failure_record = JobFailureModel(
                job_id=job_id,
                failure_stage=job_type.value,
                error_message=error_msg,
                retry_count=current_retry,
                worker_name=worker_name
            )
            session.add(failure_record)
            await session.commit()

        # 4. Check retry policies
        if retry_manager.should_retry(current_retry, max_retries):
            next_retry = current_retry + 1
            backoff_delay = retry_manager.calculate_backoff(current_retry, base_delay=base_delay)
            logger.info(f"🔄 Scheduling retry {next_retry}/{max_retries} for job {job_id} in {backoff_delay} seconds...")

            # Update retry count and set back to QUEUED
            async with db_manager.session_factory() as session:
                db_job = await session.get(PipelineJobModel, job_id)
                if db_job:
                    db_job.retry_count = next_retry
                    db_job.status = JobStatus.QUEUED.value
                    db_job.updated_at = datetime.utcnow()
                    await session.commit()

            # Re-enqueue in RQ with delay
            queue_name = f"{job_type.value}_queue"
            rq_queue = queue_manager.get_queue(queue_name)
            func_path = f"ai.workflows.workers.{job_type.value}_worker.process_job"
            
            rq_queue.enqueue_in(
                timedelta(seconds=backoff_delay),
                func_path,
                args=(job_id, workflow_id, payload),
                job_id=job_id,
                timeout=3600,
                result_ttl=86400
            )
        else:
            # 5. Move to Dead Letter Queue (DLQ)
            logger.error(f"💀 Job {job_id} has exceeded max retries. Moving to DLQ.")
            await dead_letter_queue.move_to_dead_letter(
                job_id=job_id,
                error_message=error_msg,
                payload={"job_type": job_type.value, "workflow_id": workflow_id, "priority": "normal", "payload": payload, "retry_count": current_retry}
            )

        raise e
