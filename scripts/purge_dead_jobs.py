import os
import sys
import asyncio
import argparse
import logging
from sqlalchemy import delete

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from db.repositories.manager import db_manager
from db.models.queue import DeadLetterJobModel, PipelineJobModel, JobFailureModel

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("purge_dead_jobs")

async def purge_all():
    """Purges all dead letters, job failures, and resets dead jobs."""
    async with db_manager.session_factory() as session:
        # Delete dead letters
        logger.info("Purging Dead Letter Queue table...")
        await session.execute(delete(DeadLetterJobModel))
        
        # Delete job failures
        logger.info("Purging Job Failures table...")
        await session.execute(delete(JobFailureModel))
        
        # Optional: Delete all jobs that are failed or dead
        logger.info("Deleting all failed or dead pipeline jobs...")
        await session.execute(delete(PipelineJobModel).where(PipelineJobModel.status.in_(["failed", "dead"])))
        
        await session.commit()
    logger.info("Purge complete!")

def main():
    parser = argparse.ArgumentParser(description="Purge dead letter queue and error logs.")
    parser.add_argument("--confirm", action="store_true", help="Confirm purging all failed/dead records.")
    args = parser.parse_args()

    if not args.confirm:
        logger.warning("This will permanently delete all DLQ records and failed job logs!")
        logger.warning("Run again with --confirm to proceed.")
        return
        
    loop = asyncio.get_event_loop()
    loop.run_until_complete(purge_all())

if __name__ == "__main__":
    main()
