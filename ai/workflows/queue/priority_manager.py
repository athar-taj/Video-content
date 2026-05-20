from typing import Dict, Any
from ai.workflows.queue.models import JobPriority

class PriorityManager:
    """Assigns queue priority to jobs based on viral, emotional, and retention scores."""

    def determine_priority(self, metadata: Dict[str, Any]) -> JobPriority:
        """Calculates and returns priority based on scoring metadata.
        Scores range 0-100.
        """
        viral_score = metadata.get("viral_score", 0)
        emotional_score = metadata.get("emotional_score", 0)
        retention_score = metadata.get("retention_score", 0)
        
        # Premium/Urgent: Very high scores
        if viral_score >= 95 or emotional_score >= 95:
            return JobPriority.URGENT
            
        if viral_score >= 85 or retention_score >= 85:
            return JobPriority.PREMIUM
            
        if viral_score >= 70 or emotional_score >= 75:
            return JobPriority.HIGH
            
        if viral_score < 30 and emotional_score < 30:
            return JobPriority.LOW
            
        return JobPriority.NORMAL

# Singleton instance
priority_manager = PriorityManager()
