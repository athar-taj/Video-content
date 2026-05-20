import asyncio
import logging
from typing import Dict, Any, Optional
from rq.job import Job
from rq.exceptions import NoSuchJobError

from ai.workflows.queue.queue_manager import queue_manager
from ai.workflows.queue.models import JobStatus
from db.repositories.manager import db_manager
from db.models.queue import PipelineJobModel

logger = logging.getLogger(__name__)

class JobTracker:
    """Tracks and polls job execution states."""

    async def get_job_status(self, job_id: str) -> JobStatus:
        """Determines the current status of a job from Redis or database fallback."""
        # 1. Try fetching from Redis (active state source)
        try:
            redis_conn = queue_manager.get_redis_connection()
            rq_job = Job.fetch(job_id, connection=redis_conn)
            
            # Map RQ status to our JobStatus enum
            status_map = {
                "queued": JobStatus.QUEUED,
                "started": JobStatus.ACTIVE,
                "finished": JobStatus.COMPLETED,
                "failed": JobStatus.FAILED,
                "deferred": JobStatus.PENDING,
            }
            rq_status = rq_job.get_status()
            if rq_status in status_map:
                return status_map[rq_status]
        except NoSuchJobError:
            # Job might have expired or not yet reached Redis (extremely rare race condition)
            pass
        except Exception as e:
            logger.warning(f"Error checking Redis for job {job_id}: {e}")

        # 2. Fall back to PostgreSQL database
        async with db_manager.session_factory() as session:
            db_job = await session.get(PipelineJobModel, job_id)
            if db_job:
                return JobStatus(db_job.status)
        
        return JobStatus.PENDING

    async def get_job_result(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves the result payload of a completed job."""
        # Try fetching from Redis first
        try:
            redis_conn = queue_manager.get_redis_connection()
            rq_job = Job.fetch(job_id, connection=redis_conn)
            if rq_job.is_finished:
                # RQ job results are returned from the execution function
                # If result is a dict, we return it
                res = rq_job.result
                if isinstance(res, dict):
                    return res
        except Exception:
            pass

        # Fall back to database payload/snapshot
        async with db_manager.session_factory() as session:
            db_job = await session.get(PipelineJobModel, job_id)
            if db_job and db_job.status == JobStatus.COMPLETED.value:
                # If worker saved result payload back into PipelineJobModel
                # Let's say worker saves the output result in the payload field or as a JSON metadata
                return db_job.payload.get("result") if db_job.payload else None

        return None

    async def await_job_completion(
        self,
        job_id: str,
        timeout_sec: float = 3600.0,
        check_interval_sec: float = 1.0
    ) -> Dict[str, Any]:
        """Awaits job completion by polling job status.
        Raises RuntimeError if job fails, or TimeoutError if timeout is exceeded.
        """
        start_time = asyncio.get_event_loop().time()
        
        while True:
            status = await self.get_job_status(job_id)
            
            if status == JobStatus.COMPLETED:
                result = await self.get_job_result(job_id)
                if result is not None:
                    return result
                else:
                    # Job completed but returned no result
                    return {}
            
            if status in (JobStatus.FAILED, JobStatus.DEAD):
                # Retrieve failure reason from DB using a direct select query to avoid lazy load issues
                async with db_manager.session_factory() as session:
                    from db.models.queue import JobFailureModel
                    from sqlalchemy import select
                    stmt = select(JobFailureModel).where(JobFailureModel.job_id == job_id).order_by(JobFailureModel.created_at.desc())
                    res = await session.execute(stmt)
                    last_failure = res.scalars().first()
                    errors = last_failure.error_message if last_failure else "Unknown worker failure"
                    raise RuntimeError(f"Job {job_id} failed: {errors}")

            # Check timeout
            elapsed = asyncio.get_event_loop().time() - start_time
            if elapsed >= timeout_sec:
                raise TimeoutError(f"Job {job_id} timed out after {timeout_sec} seconds")
                
            await asyncio.sleep(check_interval_sec)

# Singleton instance
job_tracker = JobTracker()
