import logging
from typing import Dict, Any, List
import os
import json

logger = logging.getLogger(__name__)

class RetentionMemory:
    """Tracks and registers user retention and performance metrics for optimization."""
    
    def __init__(self, memory_file: str = "assets/memory/retention_analytics.json"):
        self.memory_file = memory_file
        self.analytics_history: List[Dict[str, Any]] = []
        self._load_analytics()

    def _load_analytics(self):
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, "r") as f:
                    self.analytics_history = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load retention memory: {e}")

    def save_analytics(self):
        os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
        try:
            with open(self.memory_file, "w") as f:
                json.dump(self.analytics_history, f, indent=4)
        except Exception as e:
            logger.error(f"Failed to save retention memory: {e}")

    def record_metrics(self, job_id: str, metrics: Dict[str, Any]):
        """Record video metrics (retention, watch time, CTR, etc.) for a workflow job."""
        record = {
            "job_id": job_id,
            "timestamp": metrics.get("timestamp"),
            "retention_rate": metrics.get("retention_rate", 0.0),
            "watch_time_sec": metrics.get("watch_time_sec", 0.0),
            "ctr": metrics.get("ctr", 0.0),
            "narration_provider": metrics.get("narration_provider"),
            "subtitle_style": metrics.get("subtitle_style"),
            "niche": metrics.get("niche")
        }
        self.analytics_history.append(record)
        self.save_analytics()
        logger.info(f"Recorded performance metrics for job {job_id}.")

    def get_performance_by_niche(self, niche: str) -> Dict[str, Any]:
        """Calculates average performance metrics for a specific niche."""
        niche_records = [r for r in self.analytics_history if r.get("niche") == niche]
        if not niche_records:
            return {"avg_retention": 0.5, "avg_ctr": 0.05} # Baseline defaults
            
        total_ret = sum(r.get("retention_rate", 0.0) for r in niche_records)
        total_ctr = sum(r.get("ctr", 0.0) for r in niche_records)
        
        return {
            "avg_retention": total_ret / len(niche_records),
            "avg_ctr": total_ctr / len(niche_records),
            "total_videos": len(niche_records)
        }

retention_memory = RetentionMemory()
