import logging
from typing import Dict, Any
from ai.workflows.queue.models import JobType

logger = logging.getLogger(__name__)

class QueueRouter:
    """Routes jobs dynamically based on their type and resource requirements."""

    def route_job(self, job_type: JobType, payload: Dict[str, Any]) -> str:
        """Determines the target Redis queue name.
        Isolates rendering heavy loads from general orchestration logic.
        """
        if job_type == JobType.RENDER:
            # Render jobs go to the dedicated render queue
            # (which is processed by isolated render workers)
            return "render_queue"
        elif job_type == JobType.TTS:
            return "tts_queue"
        elif job_type == JobType.SUBTITLE:
            return "subtitle_queue"
        elif job_type == JobType.SCRIPT:
            return "script_queue"
        elif job_type == JobType.UPLOAD:
            return "upload_queue"
        elif job_type == JobType.ANALYTICS:
            return "analytics_queue"
            
        return "general_queue"

# Singleton instance
queue_router = QueueRouter()
