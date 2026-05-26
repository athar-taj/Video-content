import logging
import uuid
import json
import aio_pika
from typing import Dict, Any, Optional
from datetime import datetime

from ai.workflows.queue.rabbitmq_manager import rabbitmq_manager
from ai.workflows.queue.models import JobType, JobPriority, JobStatus
from ai.workflows.queue.validators import validate_job_payload
from db.repositories.manager import db_manager
from db.models.queue import PipelineJobModel

logger = logging.getLogger(__name__)

class JobDispatcher:
    """Dispatches workflow jobs to RabbitMQ exchanges and persists state in PostgreSQL."""

    @staticmethod
    def _get_routing_key(job_type: JobType) -> str:
        """Determines RabbitMQ routing key for a given job type."""
        if job_type == JobType.RENDER:
            return "render"
        elif job_type == JobType.ANALYTICS:
            return "analytics"
        else:
            return "general"

    @staticmethod
    def _get_queue_name(job_type: JobType) -> str:
        """Determines PostgreSQL queue name for tracking (consolidated to general, render, analytics)."""
        if job_type == JobType.RENDER:
            return "render_queue"
        elif job_type == JobType.ANALYTICS:
            return "analytics_queue"
        else:
            return "general_queue"

    async def dispatch(
        self,
        job_type: JobType,
        workflow_id: str,
        payload: Dict[str, Any],
        priority: JobPriority = JobPriority.NORMAL,
        max_retries: int = 3,
        backoff_factor: float = 2.0
    ) -> str:
        """Stages a job in the database, validates it, and dispatches it to RabbitMQ."""
        job_id = f"job_{uuid.uuid4().hex}"
        queue_name = self._get_queue_name(job_type)
        routing_key = self._get_routing_key(job_type)

        # 1. Validate payload
        is_valid, err_msg = validate_job_payload(job_type, payload)
        if not is_valid:
            logger.error(f"Payload validation failed for job {job_id}: {err_msg}")
            raise ValueError(f"Invalid payload: {err_msg}")

        # 2. Create database entry (Staging phase)
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

        try:
            # 3. Connect to RabbitMQ (handles reconnect silently if already connected)
            await rabbitmq_manager.connect()

            # 4. Construct message payload
            message_body = {
                "job_id": job_id,
                "workflow_id": workflow_id,
                "job_type": job_type.value,
                "priority": priority.value,
                "payload": payload,
                "retry_count": 0,
                "max_retries": max_retries,
                "backoff_factor": backoff_factor,
                "created_at": datetime.utcnow().isoformat()
            }

            # Map priority to RabbitMQ message priority property
            priority_val = 0
            if priority == JobPriority.HIGH:
                priority_val = 5
            elif priority == JobPriority.PREMIUM:
                priority_val = 8
            elif priority == JobPriority.URGENT:
                priority_val = 9

            # 5. Publish to Exchange
            message = aio_pika.Message(
                body=json.dumps(message_body).encode(),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                priority=priority_val,
                headers={"job_id": job_id}
            )

            await rabbitmq_manager.exchange.publish(
                message,
                routing_key=routing_key
            )

            logger.info(f"[QUEUE] Job queued → {job_type.value} ({job_id}) on {queue_name} (routing: {routing_key})")

            # 6. Update database status to queued
            async with db_manager.session_factory() as session:
                db_job = await session.get(PipelineJobModel, job_id)
                if db_job:
                    db_job.status = JobStatus.QUEUED.value
                    await session.commit()

            return job_id

        except Exception as e:
            logger.exception(f"Failed to publish job {job_id} to RabbitMQ: {e}")
            # Mark database entry as failed
            async with db_manager.session_factory() as session:
                db_job = await session.get(PipelineJobModel, job_id)
                if db_job:
                    db_job.status = JobStatus.FAILED.value
                    await session.commit()
            raise e

# Singleton instance
job_dispatcher = JobDispatcher()
