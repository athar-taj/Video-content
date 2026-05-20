import os
import sys
import argparse
import time
import threading
import asyncio
import logging
from rq import SimpleWorker

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from shared.config.settings import settings
from ai.workflows.queue.queue_manager import queue_manager
from ai.workflows.queue.worker_registry import worker_registry
from ai.workflows.queue.models import WorkerStatus

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("run_worker")

def start_heartbeat_loop(worker_name: str, queue_name: str, worker_obj: SimpleWorker):
    """Runs a background thread sending periodic heartbeats to PostgreSQL."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # Create thread-local dedicated database engine and session factory to avoid sharing connection pools across event loops/threads
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG,
        pool_pre_ping=True
    )
    session_factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    # 1. Register worker
    loop.run_until_complete(worker_registry.register_worker(worker_name, queue_name, session_factory))
    
    while True:
        try:
            # Determine status based on local worker state to avoid Redis contention
            status = WorkerStatus.IDLE
            active_jobs = []
            
            # Use local current_job attribute (does not call Redis network)
            current_job = getattr(worker_obj, "_current_job", None) or getattr(worker_obj, "current_job", None)
            if current_job:
                status = WorkerStatus.BUSY
                active_jobs = [current_job.id]
            elif getattr(worker_obj, "state", "") == "busy":
                status = WorkerStatus.BUSY
                
            loop.run_until_complete(worker_registry.update_heartbeat(worker_name, status, active_jobs, session_factory))
        except Exception as e:
            logger.error(f"Heartbeat failed: {e}")
            
        time.sleep(15)

def main():
    parser = argparse.ArgumentParser(description="Start a general RQ Worker on Windows.")
    parser.add_argument(
        "--queues", 
        nargs="+", 
        default=["script_queue", "tts_queue", "subtitle_queue", "upload_queue", "analytics_queue"],
        help="Queue names to listen on."
    )
    parser.add_argument("--name", type=str, default=None, help="Worker identifier name.")
    args = parser.parse_args()

    worker_name = args.name or f"general_worker_{os.getpid()}"
    os.environ["WORKER_NAME"] = worker_name
    
    # Listen to specified queues
    queues = [queue_manager.get_queue(q_name) for q_name in args.queues]
    queue_names_str = ", ".join(args.queues)
    
    logger.info(f"Starting worker {worker_name} listening on: {queue_names_str}")
    
    # On Windows, we use SimpleWorker which runs jobs in-process (no fork)
    # We pass the connection directly to SimpleWorker constructor
    worker = SimpleWorker(queues, connection=queue_manager.get_redis_connection(), name=worker_name)
    
    # Start heartbeat background thread
    hb_thread = threading.Thread(
        target=start_heartbeat_loop,
        args=(worker_name, queue_names_str, worker),
        daemon=True
    )
    hb_thread.start()
    
    # Start working
    worker.work()

if __name__ == "__main__":
    main()
