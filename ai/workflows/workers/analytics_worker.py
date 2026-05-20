import logging
import random
from typing import Dict, Any

from ai.workflows.workers.base_worker import run_async, execute_job_wrapper
from ai.workflows.queue.models import JobType

logger = logging.getLogger(__name__)

async def _process_analytics_async(job_id: str, workflow_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Asynchronous business logic for gathering and routing analytics feedback."""
    from ai.workflows.pipeline.analytics_router import AnalyticsRouter

    script_data = payload.get("generated_script", {})
    hook = script_data.get("hook", "")
    workflow_type = payload.get("workflow_type", "cheap")
    
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
        "watch_time_sec": retention * 60,
        "ctr": ctr,
        "narration_provider": payload.get("selected_tts_provider", "Unknown"),
        "subtitle_style": "karaoke",
        "niche": payload.get("execution_metadata", {}).get("subreddit", "general"),
        "hook": hook
    }
    
    router = AnalyticsRouter()
    router.route_feedback(job_id, metrics)
    
    logger.info(f"Ingested simulated feedback for {job_id}: retention={retention:.2%}, CTR={ctr:.2%}")
    return {
        "metrics": metrics
    }

def process_job(job_id: str, workflow_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """RQ target function for Analytics Worker."""
    return run_async(
        execute_job_wrapper(
            job_id=job_id,
            workflow_id=workflow_id,
            payload=payload,
            job_type=JobType.ANALYTICS,
            processor_func=_process_analytics_async
        )
    )
