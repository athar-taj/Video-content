import asyncio
import logging
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ai.workflows.pipeline.langgraph_orchestrator import LangGraphOrchestrator
from ai.workflows.pipeline.workflow_registry import WorkflowRegistry

# Setup structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("test_langgraph")

async def run_scenario(scenario_name: str, score: int):
    logger.info(f"\n==================================================")
    logger.info(f"Running Scenario: {scenario_name} (Forced Viral Score: {score})")
    logger.info(f"==================================================")
    
    registry = WorkflowRegistry()
    orchestrator = LangGraphOrchestrator(registry)
    
    job_id = f"job_{scenario_name.lower().replace(' ', '_')}"
    
    final_state = await orchestrator.execute_workflow(job_id=job_id, topic_id="test_topic", forced_score=score)
    
    logger.info(f"Final Execution Route Chosen: {final_state.get('workflow_type')}")
    logger.info(f"Generated Render Path: {final_state.get('render_output_path')}\n")

async def test_langgraph():
    # Scenario 1: Low potential topic -> routes to Cheap Pipeline
    await run_scenario("Low Potential Content", score=35)
    
    # Scenario 2: High potential topic -> routes to Premium Pipeline
    await run_scenario("High Potential Viral Content", score=95)

if __name__ == "__main__":
    # Ensure langgraph is installed
    try:
        import langgraph
    except ImportError:
        logger.error("LangGraph is not installed. Please install using: pip install langgraph")
        sys.exit(1)
        
    asyncio.run(test_langgraph())
