import logging
from datetime import datetime
from typing import Dict, Optional
from .models import PipelineJob, PipelineStatus, StageStatus, PipelineState

logger = logging.getLogger(__name__)

class StateManager:
    """Manages the persistence and state transitions of pipeline jobs."""
    
    def __init__(self):
        # In-memory storage for local execution. Replace with SQLAlchemy/Redis in prod.
        self._jobs: Dict[str, PipelineJob] = {}

    def create_job(self, topic_id: str, workflow_type: str = "default_shorts") -> PipelineJob:
        job_id = f"job_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{topic_id[:4]}"
        job = PipelineJob(
            job_id=job_id,
            topic_id=topic_id,
            workflow_type=workflow_type,
            started_at=datetime.utcnow()
        )
        self._jobs[job_id] = job
        logger.info(f"Created new pipeline job: {job_id}")
        return job

    def get_job(self, job_id: str) -> Optional[PipelineJob]:
        return self._jobs.get(job_id)

    def update_stage_status(self, job_id: str, stage_name: str, status: StageStatus):
        job = self.get_job(job_id)
        if not job:
            return
            
        logger.info(f"Job {job_id} - Stage '{stage_name}' -> {status.value}")
        
        # Update specific state field based on stage name
        state_attr = f"{stage_name}_status"
        if hasattr(job.state, state_attr):
            setattr(job.state, state_attr, status)
            
        job.current_stage = stage_name
        
        if status == StageStatus.FAILED:
            self.update_job_status(job_id, PipelineStatus.FAILED)

    def update_job_status(self, job_id: str, status: PipelineStatus):
        job = self.get_job(job_id)
        if not job:
            return
            
        logger.info(f"Job {job_id} -> {status.value}")
        job.status = status
        
        if status in [PipelineStatus.COMPLETED, PipelineStatus.FAILED]:
            job.completed_at = datetime.utcnow()
