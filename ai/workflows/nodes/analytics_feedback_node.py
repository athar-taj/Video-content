import logging
import random
from typing import Dict, Any
from ai.workflows.pipeline.analytics_router import AnalyticsRouter

logger = logging.getLogger(__name__)

async def analytics_feedback_node(state: Dict[str, Any]) -> Dict[str, Any]:
    logger.info("Executing Analytics Feedback Node...")
    
    job_id = state.get("job_id")
    script_data = state.get("generated_script", {})
    hook = script_data.get("hook", "")
    provider = state.get("selected_llm_provider", "Unknown")
    
    # Simulate high performance if it was a premium video
    workflow_type = state.get("workflow_type", "cheap")
    if workflow_type == "premium":
        retention = random.uniform(0.70, 0.90)
        ctr = random.uniform(0.08, 0.15)
    elif workflow_type == "balanced":
        retention = random.uniform(0.55, 0.75)
        ctr = random.uniform(0.05, 0.10)
    else:
        retention = random.uniform(0.35, 0.60)
        ctr = random.uniform(0.02, 0.07)
        
    metrics = {
        "timestamp": "2026-05-19T10:00:00Z",
        "retention_rate": retention,
        "watch_time_sec": retention * 60, # Assuming 60s video
        "ctr": ctr,
        "narration_provider": state.get("selected_tts_provider", "Unknown"),
        "subtitle_style": "karaoke",
        "niche": state.get("execution_metadata", {}).get("subreddit", "general"),
        "hook": hook
    }
    
    router = AnalyticsRouter()
    router.route_feedback(job_id, metrics)
    
    logger.info(f"Ingested simulated feedback for {job_id}: retention={retention:.2%}, CTR={ctr:.2%}")
    return {}
