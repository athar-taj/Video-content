import os
import sys
import asyncio
import argparse
import logging

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from db.repositories.manager import db_manager
from db.models.queue import PipelineJobModel, DeadLetterJobModel
from ai.workflows.queue.models import JobStatus, JobType
from ai.workflows.queue.job_dispatcher import job_dispatcher
from ai.workflows.queue.dead_letter_queue import dead_letter_queue

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("retry_failed_jobs")

async def list_failed_jobs():
    """Lists all failed or dead jobs from database."""
    from sqlalchemy import select
    async with db_manager.session_factory() as session:
        # Failed/Dead jobs
        stmt = select(PipelineJobModel).where(PipelineJobModel.status.in_([JobStatus.FAILED.value, JobStatus.DEAD.value]))
        result = await session.execute(stmt)
        jobs = result.scalars().all()
        
        logger.info(f"--- FAILED AND DEAD JOBS ({len(jobs)}) ---")
        for j in jobs:
            logger.info(f"ID: {j.id} | Workflow: {j.workflow_id} | Stage: {j.current_stage} | Status: {j.status} | Retries: {j.retry_count}")

        # DLQ jobs
        dlq_jobs = await dead_letter_queue.get_dead_jobs()
        logger.info(f"\n--- DEAD LETTER QUEUE (DLQ) RECORDS ({len(dlq_jobs)}) ---")
        for dj in dlq_jobs:
            logger.info(f"DLQ ID: {dj['id']} | Original ID: {dj['original_job_id']} | Reason: {dj['failure_reason']}")

async def retry_job_by_id(job_id: str):
    """Retries a specific failed job."""
    from sqlalchemy import select
    async with db_manager.session_factory() as session:
        db_job = await session.get(PipelineJobModel, job_id)
        if not db_job:
            logger.error(f"Job {job_id} not found.")
            return
            
        if db_job.status not in [JobStatus.FAILED.value, JobStatus.DEAD.value]:
            logger.warning(f"Job {job_id} is in '{db_job.status}' state. Cannot retry.")
            return

        payload = db_job.payload or {}
        workflow_id = db_job.workflow_id
        job_type = JobType(db_job.current_stage)
        
        logger.info(f"Retrying Job {job_id} ({job_type.value})...")
        
        # Reset retries in database
        db_job.retry_count = 0
        db_job.status = JobStatus.PENDING.value
        await session.commit()
        
    # Re-dispatch
    new_job_id = await job_dispatcher.dispatch(
        job_type=job_type,
        workflow_id=workflow_id,
        payload=payload,
        priority=payload.get("priority", "normal")
    )
    logger.info(f"Re-dispatched. New job ID: {new_job_id}")

async def replay_dlq_by_id(dlq_id: int):
    """Replays a DLQ job by its record ID."""
    logger.info(f"Replaying DLQ record ID: {dlq_id}...")
    new_job_id = await dead_letter_queue.replay_job(dlq_id)
    if new_job_id:
        logger.info(f"Replayed successfully. New job ID: {new_job_id}")
    else:
        logger.error(f"Replay failed for DLQ ID: {dlq_id}")

def main():
    parser = argparse.ArgumentParser(description="Retry failed or Dead Letter Queue jobs.")
    parser.add_argument("--list", action="store_true", help="List all failed and dead jobs.")
    parser.add_argument("--retry", type=str, help="Retry a failed job by its ID.")
    parser.add_argument("--replay-dlq", type=int, help="Replay a Dead Letter Queue job by its DLQ record ID.")
    args = parser.parse_args()

    loop = asyncio.get_event_loop()
    
    if args.list:
        loop.run_until_complete(list_failed_jobs())
    elif args.retry:
        loop.run_until_complete(retry_job_by_id(args.retry))
    elif args.replay_dlq is not None:
        loop.run_until_complete(replay_dlq_by_id(args.replay_dlq))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
