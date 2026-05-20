import logging
from typing import Dict, Any, List
from rq.queue import Queue
from rq.registry import StartedJobRegistry, FailedJobRegistry

from ai.workflows.queue.queue_manager import queue_manager
from ai.workflows.queue.models import JobType
from db.repositories.manager import db_manager
from db.models.queue import PipelineJobModel, JobFailureModel

logger = logging.getLogger(__name__)

class QueueMetrics:
    """Collects queue execution throughput, depth, and error rates."""

    def get_queue_depths(self) -> Dict[str, int]:
        """Calculates queue lengths for all job type queues in Redis."""
        depths = {}
        for job_type in JobType:
            queue_name = f"{job_type.value}_queue"
            try:
                q = queue_manager.get_queue(queue_name)
                depths[queue_name] = len(q)
            except Exception as e:
                logger.warning(f"Failed to get depth for queue {queue_name}: {e}")
                depths[queue_name] = 0
        return depths

    async def get_database_metrics(self) -> Dict[str, Any]:
        """Queries the database to count jobs in various statuses."""
        from sqlalchemy import select, func
        
        metrics = {
            "pending": 0,
            "queued": 0,
            "active": 0,
            "completed": 0,
            "failed": 0,
            "dead": 0,
            "total_jobs": 0,
            "total_failures": 0
        }
        
        async with db_manager.session_factory() as session:
            # Count jobs by status
            stmt = select(PipelineJobModel.status, func.count(PipelineJobModel.id)).group_by(PipelineJobModel.status)
            result = await session.execute(stmt)
            for status, count in result.all():
                if status in metrics:
                    metrics[status] = count
            
            # Get total jobs
            stmt_total = select(func.count(PipelineJobModel.id))
            metrics["total_jobs"] = await session.fetchval(stmt_total) or 0
            
            # Get total failures logged
            stmt_failures = select(func.count(JobFailureModel.id))
            metrics["total_failures"] = await session.fetchval(stmt_failures) or 0
            
        return metrics

    async def get_full_dashboard_metrics(self) -> Dict[str, Any]:
        """Aggregates Redis-level and PostgreSQL-level metrics for dashboard monitoring."""
        db_metrics = await self.get_database_metrics()
        depths = self.get_queue_depths()
        
        return {
            "queue_depths": depths,
            "db_job_states": db_metrics,
            "timestamp": dict(now=logging.Formatter().formatTime(logging.LogRecord('', 0, '', 0, '', (), None)))
        }

# Singleton instance
queue_metrics = QueueMetrics()
