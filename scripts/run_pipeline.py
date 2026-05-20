import asyncio
import logging
import sys
import os

# Ensure the root project directory is in the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ai.workflows.pipeline.langgraph_orchestrator import LangGraphOrchestrator
from ai.workflows.pipeline.workflow_registry import WorkflowRegistry

# Setup structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("Zem.RunPipeline")

async def main():
    logger.info("==================================================")
    logger.info("Starting Zem Autonomous AI Media Operating System")
    logger.info("==================================================")

    # Initialize the workflow registry and the LangGraph Autonomous Brain
    registry = WorkflowRegistry()
    orchestrator = LangGraphOrchestrator(registry)
    
    # In production, this data comes from the discovery module (Reddit)
    import uuid
    job_id = f"job_auto_{uuid.uuid4().hex[:8]}"
    topic_id = "topic_reddit_gaming_001"
    
    logger.info(f"Triggering Autonomous Pipeline for Topic: {topic_id}")
    
    try:
        # We simulate a "Balanced" post with a score of 65
        final_state = await orchestrator.execute_workflow(
            job_id=job_id, 
            topic_id=topic_id, 
            forced_score=65
        )
        
        if final_state.get('render_output_path'):
            logger.info("==================================================")
            logger.info(f"PIPELINE SUCCESS!")
            logger.info(f"Video Output: {final_state['render_output_path']}")
            logger.info(f"Workflow Route Executed: {final_state['workflow_type'].upper()}")
            logger.info("==================================================")
        else:
            logger.error("Pipeline Failed to yield a video.")
            
    except Exception as e:
        logger.error(f"Pipeline Execution crashed critically: {str(e)}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(main())
