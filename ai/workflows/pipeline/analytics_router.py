import logging
from typing import Dict, Any
from ai.workflows.memory.retention_memory import retention_memory
from ai.workflows.memory.workflow_learning_memory import workflow_learning_memory

logger = logging.getLogger(__name__)

class AnalyticsRouter:
    """Routes incoming analytics/feedback metrics to the respective memory buffers."""
    
    def route_feedback(self, job_id: str, feedback_metrics: Dict[str, Any]):
        """Ingest video performance metrics and update learning + retention history."""
        logger.info(f"Routing analytics feedback for job {job_id}...")
        
        # 1. Update retention statistics
        retention_memory.record_metrics(job_id, feedback_metrics)
        
        # 2. If it's a high-performance video, teach workflow memory
        retention_rate = feedback_metrics.get("retention_rate", 0.0)
        ctr = feedback_metrics.get("ctr", 0.0)
        
        # Consider viral / successful if retention is > 65% and CTR is > 8%
        if retention_rate >= 0.65 and ctr >= 0.08:
            logger.info(f"Job {job_id} scored high in analytics! Recording as a learning point.")
            workflow_learning_memory.record_successful_run(
                hook=feedback_metrics.get("hook", ""),
                provider=feedback_metrics.get("narration_provider", "Unknown"),
                narration_style=feedback_metrics.get("subtitle_style", "default")
            )
            
    def get_optimizations(self, niche: str) -> Dict[str, Any]:
        """Calculates current recommendation suggestions based on history and metrics."""
        recommendations = workflow_learning_memory.get_recommendations()
        niche_stats = retention_memory.get_performance_by_niche(niche)
        
        return {
            "niche": niche,
            "performance": niche_stats,
            "recommendations": recommendations
        }
