import asyncio
import logging
from typing import Dict, Any, Optional

from ai.workflows.queue.models import JobStatus
from db.repositories.manager import db_manager
from db.models.queue import PipelineJobModel

logger = logging.getLogger(__name__)

class JobTracker:
    """Tracks and polls job execution states via the database staging layer."""

    async def get_job_status(self, job_id: str) -> JobStatus:
        """Determines the current status of a job from the database."""
        async with db_manager.session_factory() as session:
            db_job = await session.get(PipelineJobModel, job_id)
            if db_job:
                return JobStatus(db_job.status)
        return JobStatus.PENDING

    async def get_job_result(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves the result payload of a completed job from the database."""
        async with db_manager.session_factory() as session:
            db_job = await session.get(PipelineJobModel, job_id)
            if db_job and db_job.status == JobStatus.COMPLETED.value:
                # Retrieve the result saved in the payload by the worker
                if db_job.payload and isinstance(db_job.payload, dict):
                    return db_job.payload.get("result")
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
                    return {}
            
            if status in (JobStatus.FAILED, JobStatus.DEAD):
                # Retrieve failure reason from DB
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
