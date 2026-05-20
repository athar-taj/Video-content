import asyncio
import logging
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ai.workflows.pipeline import WorkflowOrchestrator, PipelineStatus

# Setup structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("test_pipeline")

async def test_pipeline():
    logger.info("Executing test_pipeline.py")
    
    topic_id = "test_horror_topic"
    topic_data = {
        "title": "Scary basement story",
        "niche": "horror"
    }
    
    try:
        orchestrator = WorkflowOrchestrator()
        
        logger.info("Starting orchestrated pipeline workflow...")
        job = await orchestrator.run_default_workflow(topic_id, topic_data)
        
        if job.status == PipelineStatus.COMPLETED:
            logger.info("Test passed. Pipeline successfully executed all stages.")
            print(f"\n=== TEST SUCCESS: Job {job.job_id} Completed ===")
            print(f"Final state: {job.state.model_dump()}")
            print("============================================\n")
        else:
            logger.error(f"Test failed. Pipeline stopped at stage: {job.current_stage}")
            
    except Exception as e:
        logger.error(f"Test failed with exception: {str(e)}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(test_pipeline())
