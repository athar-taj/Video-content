import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

async def workflow_router_node(state: Dict[str, Any]) -> Dict[str, Any]:
    logger.info("Executing Workflow Router Node...")
    
    viral_score = state.get("viral_score", 0)
    
    if viral_score < 40:
        workflow_type = "rejected"
        workflow_status = "rejected"
    elif 40 <= viral_score <= 75:
        workflow_type = "balanced"
        workflow_status = "running"
    else:
        workflow_type = "premium"
        workflow_status = "running"
        
    logger.info(f"Router Decision: score={viral_score} -> route={workflow_type}, status={workflow_status}")
    return {
        "workflow_type": workflow_type,
        "workflow_status": workflow_status
    }
