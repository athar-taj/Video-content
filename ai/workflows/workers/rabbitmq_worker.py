import os
import sys
import argparse
import asyncio
import logging
import json
import importlib
from datetime import datetime
import aio_pika

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from shared.config.settings import settings
from ai.workflows.queue.rabbitmq_manager import rabbitmq_manager
from ai.workflows.queue.worker_registry import worker_registry
from ai.workflows.queue.models import WorkerStatus, JobStatus, JobType
from ai.workflows.queue.dead_letter_queue import dead_letter_queue
from db.repositories.manager import db_manager
from db.models.queue import PipelineJobModel, JobFailureModel

# Set up logging for workers to write cleanly to stdout
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("rabbitmq_worker")

class RabbitMQWorker:
    """Consumes tasks from a RabbitMQ queue and manages workflow execution, retries, and database telemetry."""
    
    def __init__(self, worker_name: str, queue_name: str, routing_key: str):
        self.worker_name = worker_name
        self.queue_name = queue_name
        self.routing_key = routing_key
        self.active_jobs = []
        self.status = WorkerStatus.IDLE
        self._running = False

    async def start(self):
        """Starts connection, registers worker, launches heartbeat, and begins consuming."""
        self._running = True
        logger.info(f"[{self.worker_name}] 🚀 Starting worker for queue {self.queue_name}...")
        
        # 1. Connect to RabbitMQ topology
        await rabbitmq_manager.connect()
        
        # 2. Register worker in DB
        await worker_registry.register_worker(self.worker_name, self.queue_name)
        
        # 3. Start heartbeat loop as background task
        asyncio.create_task(self.heartbeat_loop())
        
        # 4. Begin consuming
        channel = rabbitmq_manager.channel
        await channel.set_qos(prefetch_count=5)
        
        queue = await channel.get_queue(self.queue_name)
        logger.info(f"[{self.worker_name}] Listening for messages on {self.queue_name}...")
        
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                if not self._running:
                    break
                # Process message concurrently without blocking the consumer iterator
                asyncio.create_task(self.process_message(message))

    async def heartbeat_loop(self):
        """Periodically reports worker heartbeat to PostgreSQL database."""
        while self._running:
            try:
                await worker_registry.update_heartbeat(
                    worker_name=self.worker_name,
                    status=self.status,
                    active_jobs=self.active_jobs
                )
            except Exception as e:
                logger.error(f"[{self.worker_name}] Heartbeat failed: {e}")
            await asyncio.sleep(15)

    async def process_message(self, message: aio_pika.IncomingMessage):
        """Parses RabbitMQ message, updates execution states, routes task execution, and executes retries."""
        async with message.process(requeue=False):
            job_id = None
            try:
                body = json.loads(message.body.decode())
                job_id = body.get("job_id")
                workflow_id = body.get("workflow_id")
                job_type_str = body.get("job_type")
                payload = body.get("payload", {})
                retry_count = body.get("retry_count", 0)
                max_retries = body.get("max_retries", 3)
                backoff_factor = body.get("backoff_factor", 2.0)
                
                logger.info(f"[{self.worker_name}] Received task: {job_type_str} ({job_id}) on {self.queue_name}")
                
                self.active_jobs.append(job_id)
                self.status = WorkerStatus.BUSY
                
                # 1. Update job to ACTIVE in database
                async with db_manager.session_factory() as session:
                    db_job = await session.get(PipelineJobModel, job_id)
                    if db_job:
                        db_job.status = JobStatus.ACTIVE.value
                        db_job.assigned_worker = self.worker_name
                        db_job.updated_at = datetime.utcnow()
                        await session.commit()
                
                # 2. Dynamically import and execute target module
                logger.info(f"[{self.worker_name}] Processing {job_type_str} job...")
                module = importlib.import_module(f"ai.workflows.workers.{job_type_str}_worker")
                processor_func = getattr(module, f"_process_{job_type_str}_async")
                
                result = await processor_func(job_id, workflow_id, payload)
                
                # 3. Handle success - update database
                async with db_manager.session_factory() as session:
                    db_job = await session.get(PipelineJobModel, job_id)
                    if db_job:
                        db_job.status = JobStatus.COMPLETED.value
                        payload_updated = dict(db_job.payload or {})
                        payload_updated["result"] = result
                        db_job.payload = payload_updated
                        db_job.updated_at = datetime.utcnow()
                        await session.commit()
                
                logger.info(f"[{self.worker_name}] ✅ {job_type_str.capitalize()} job complete ({job_id})")
                
            except Exception as e:
                error_msg = f"{type(e).__name__}: {str(e)}"
                logger.error(f"[ERROR][{self.worker_name}] Task: {job_type_str or 'unknown'} | Reason: {error_msg} | Queue: {self.queue_name} | Retry: {retry_count}/{max_retries}")
                
                if job_id:
                    # Write failure details to postgres
                    async with db_manager.session_factory() as session:
                        failure_record = JobFailureModel(
                            job_id=job_id,
                            failure_stage=job_type_str or "unknown",
                            error_message=error_msg,
                            retry_count=retry_count,
                            worker_name=self.worker_name
                        )
                        session.add(failure_record)
                        await session.commit()

                    # 4. Handle Retry Logic
                    if retry_count < max_retries:
                        next_retry = retry_count + 1
                        backoff_delay = backoff_factor ** retry_count
                        logger.info(f"[{self.worker_name}] 🔄 Scheduling retry {next_retry}/{max_retries} for job {job_id} in {backoff_delay}s...")
                        
                        # Set database status to QUEUED
                        async with db_manager.session_factory() as session:
                            db_job = await session.get(PipelineJobModel, job_id)
                            if db_job:
                                db_job.retry_count = next_retry
                                db_job.status = JobStatus.QUEUED.value
                                db_job.updated_at = datetime.utcnow()
                                await session.commit()
                        
                        # Re-publish message after async backoff delay
                        await asyncio.sleep(backoff_delay)
                        
                        body["retry_count"] = next_retry
                        message_to_send = aio_pika.Message(
                            body=json.dumps(body).encode(),
                            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                            headers={"job_id": job_id}
                        )
                        
                        await rabbitmq_manager.exchange.publish(
                            message_to_send,
                            routing_key=self.routing_key
                        )
                    else:
                        # 5. Move to Dead Letter Queue (DLQ)
                        logger.error(f"[{self.worker_name}] 💀 Job {job_id} has exceeded max retries. Routing to DLQ.")
                        
                        # Move in DB
                        await dead_letter_queue.move_to_dead_letter(
                            job_id=job_id,
                            error_message=error_msg,
                            payload={
                                "job_type": job_type_str,
                                "workflow_id": workflow_id,
                                "priority": "normal",
                                "payload": payload,
                                "retry_count": retry_count
                            }
                        )
                        
                        # Publish to RabbitMQ DLQ
                        dlq_message = aio_pika.Message(
                            body=json.dumps(body).encode(),
                            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                            headers={"job_id": job_id, "failure_reason": error_msg}
                        )
                        await rabbitmq_manager.dlx.publish(
                            dlq_message,
                            routing_key="dead_letter"
                        )
            
            finally:
                if job_id in self.active_jobs:
                    self.active_jobs.remove(job_id)
                self.status = WorkerStatus.IDLE if not self.active_jobs else WorkerStatus.BUSY

    def stop(self):
        self._running = False

async def main():
    parser = argparse.ArgumentParser(description="Zem RabbitMQ Unified Worker Daemon.")
    parser.add_argument("--queue", type=str, required=True, choices=["general_queue", "render_queue", "analytics_queue"], help="Target queue name to consume from.")
    parser.add_argument("--name", type=str, default=None, help="Custom identifier name for the worker.")
    args = parser.parse_args()
    
    routing_map = {
        "general_queue": "general",
        "render_queue": "render",
        "analytics_queue": "analytics"
    }
    
    worker_id = args.name or f"{args.queue.split('_')[0]}_worker_{os.getpid()}"
    os.environ["WORKER_NAME"] = worker_id
    
    worker = RabbitMQWorker(
        worker_name=worker_id,
        queue_name=args.queue,
        routing_key=routing_map[args.queue]
    )
    
    try:
        await worker.start()
    except KeyboardInterrupt:
        logger.info(f"[{worker_id}] Shutting down gracefully...")
        worker.stop()
        await rabbitmq_manager.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
