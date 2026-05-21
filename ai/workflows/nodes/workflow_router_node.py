import logging
import os
from typing import Dict, Any
from shared.config.settings import settings
from ai.workflows.pipeline.provider_capability_registry import provider_capability_registry

logger = logging.getLogger(__name__)

async def workflow_router_node(state: Dict[str, Any]) -> Dict[str, Any]:
    logger.info("Executing Workflow Router Node...")
    
    viral_score = state.get("viral_score", 0)
    
    # 1. Determine base status
    if viral_score < 40:
        logger.warning(f"Workflow rejected: Viral score {viral_score} is below threshold 40.")
        return {
            "workflow_type": "rejected",
            "workflow_status": "rejected"
        }
        
    workflow_status = "running"
    
    # 2. Check provider capabilities
    openai_available = await provider_capability_registry.is_provider_available("openai")
    claude_available = await provider_capability_registry.is_provider_available("claude")
    mistral_available = await provider_capability_registry.is_provider_available("mistral")
    sarvam_available = await provider_capability_registry.is_provider_available("sarvam")
    
    premium_llm_available = openai_available or claude_available or mistral_available
    
    # 3. Detect offline/local constraints
    offline_requested = os.environ.get("OFFLINE_MODE", "false").lower() == "true" or \
                        (not settings.ENABLE_OPENAI and not settings.ENABLE_CLAUDE and 
                         not settings.ENABLE_SARVAM and not settings.ENABLE_MURF and not settings.ENABLE_HF)
                         
    # 4. Route based on score, offline mode, and API availability
    if offline_requested:
        logger.info("Offline mode detected. Routing to 'local_only_workflow'.")
        workflow_type = "local_only_workflow"
    elif not premium_llm_available:
        logger.warning("No premium LLM API keys available/enabled. Downgrading workflow.")
        if sarvam_available:
            logger.info("Sarvam TTS is available. Routing to 'hybrid_workflow'.")
            workflow_type = "hybrid_workflow"
        else:
            logger.info("No premium cloud services available. Routing to 'ultra_cheap_workflow'.")
            workflow_type = "ultra_cheap_workflow"
    else:
        # Premium/Balanced score routing
        if viral_score > 85:
            logger.info("High viral score (> 85) and premium LLMs available. Routing to 'premium_optional_workflow'.")
            workflow_type = "premium_optional_workflow"
        else:
            logger.info("Moderate viral score (<= 85). Routing to balanced path.")
            if sarvam_available:
                workflow_type = "hybrid_workflow"
            else:
                workflow_type = "ultra_cheap_workflow"
                
    logger.info(f"Router Decision: score={viral_score} -> route={workflow_type}, status={workflow_status}")
    return {
        "workflow_type": workflow_type,
        "workflow_status": workflow_status
    }
