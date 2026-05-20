import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any

from db.repositories.manager import db_manager
from db.models.queue import WorkerStateModel
from ai.workflows.queue.models import WorkerStatus

logger = logging.getLogger(__name__)

class WorkerRegistry:
    """Manages tracking of active workers and registering heartbeats in the database."""

    async def register_worker(self, worker_name: str, queue_name: str, session_factory = None) -> None:
        """Registers a worker or updates its state to idle/online when it starts."""
        from sqlalchemy import select
        factory = session_factory or db_manager.session_factory
        async with factory() as session:
            stmt = select(WorkerStateModel).where(WorkerStateModel.worker_name == worker_name)
            result = await session.execute(stmt)
            worker = result.scalar_one_or_none()
            
            if worker:
                worker.queue_name = queue_name
                worker.status = WorkerStatus.IDLE.value
                worker.active_jobs = []
                worker.last_heartbeat = datetime.utcnow()
            else:
                worker = WorkerStateModel(
                    worker_name=worker_name,
                    queue_name=queue_name,
                    status=WorkerStatus.IDLE.value,
                    active_jobs=[],
                    last_heartbeat=datetime.utcnow()
                )
                session.add(worker)
                
            await session.commit()
            logger.info(f"Registered worker: {worker_name} on queue: {queue_name}")

    async def update_heartbeat(self, worker_name: str, status: WorkerStatus, active_jobs: List[str], session_factory = None) -> None:
        """Updates worker heartbeat and active jobs list."""
        from sqlalchemy import select
        factory = session_factory or db_manager.session_factory
        async with factory() as session:
            stmt = select(WorkerStateModel).where(WorkerStateModel.worker_name == worker_name)
            result = await session.execute(stmt)
            worker = result.scalar_one_or_none()
            
            if worker:
                worker.status = status.value
                worker.active_jobs = active_jobs
                worker.last_heartbeat = datetime.utcnow()
                await session.commit()

    async def prune_offline_workers(self, timeout_seconds: int = 60) -> int:
        """Flags workers as offline if they haven't sent a heartbeat within the timeout window."""
        from sqlalchemy import select
        cutoff_time = datetime.utcnow() - timedelta(seconds=timeout_seconds)
        
        async with db_manager.session_factory() as session:
            stmt = select(WorkerStateModel).where(
                WorkerStateModel.status != WorkerStatus.OFFLINE.value,
                WorkerStateModel.last_heartbeat < cutoff_time
            )
            result = await session.execute(stmt)
            stale_workers = result.scalars().all()
            
            count = len(stale_workers)
            for worker in stale_workers:
                logger.warning(f"Worker {worker.worker_name} missed heartbeat. Setting OFFLINE.")
                worker.status = WorkerStatus.OFFLINE.value
                worker.active_jobs = []
                
            if count > 0:
                await session.commit()
            return count

# Singleton instance
worker_registry = WorkerRegistry()
