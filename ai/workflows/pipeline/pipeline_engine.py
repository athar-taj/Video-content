import logging
from typing import List, Dict, Any
from .models import PipelineStatus, StageStatus, PipelineJob
from .execution_context import ContextManager
from .state_manager import StateManager
from .retry_manager import RetryManager
from .dependency_resolver import DependencyResolver
from .validators import PipelineValidator
from .workflow_registry import WorkflowRegistry

logger = logging.getLogger(__name__)

class PipelineEngine:
    """Core orchestration engine for the AI media pipeline."""
    
    def __init__(self, registry: WorkflowRegistry):
        self.registry = registry
        self.context_manager = ContextManager()
        self.state_manager = StateManager()
        self.retry_manager = RetryManager(max_retries=3, base_backoff_seconds=2)
        self.dependency_resolver = DependencyResolver()
        self.validator = PipelineValidator()

    async def execute_stage(self, stage_name: str, job_id: str) -> bool:
        """Execute a single pipeline stage with retries and validation."""
        logger.info(f"[{job_id}] Executing stage: {stage_name}")
        
        self.state_manager.update_stage_status(job_id, stage_name, StageStatus.RUNNING)
        context = self.context_manager.get_context(job_id)
        
        # Check prerequisites
        if not self.dependency_resolver.check_prerequisites(stage_name, context):
            logger.error(f"[{job_id}] Prerequisites failed for stage: {stage_name}")
            self.state_manager.update_stage_status(job_id, stage_name, StageStatus.FAILED)
            return False

        handler = self.registry.get_handler(stage_name)
        
        try:
            # Execute with retry
            await self.retry_manager.execute_with_retry(stage_name, handler, context)
            
            # Validate output
            if not self.validator.validate_stage_output(stage_name, context):
                raise ValueError(f"Output validation failed for stage: {stage_name}")
                
            self.state_manager.update_stage_status(job_id, stage_name, StageStatus.COMPLETED)
            return True
            
        except Exception as e:
            logger.error(f"[{job_id}] Stage '{stage_name}' failed critically: {str(e)}")
            context.errors.append(str(e))
            self.state_manager.update_stage_status(job_id, stage_name, StageStatus.FAILED)
            return False

    async def execute_pipeline(self, topic_id: str, topic_data: Dict[str, Any], stages: List[str]) -> PipelineJob:
        """Execute the full end-to-end pipeline sequentially."""
        job = self.state_manager.create_job(topic_id)
        context = self.context_manager.create_context(job.job_id, topic_data)
        
        self.state_manager.update_job_status(job.job_id, PipelineStatus.RUNNING)
        logger.info(f"[{job.job_id}] Starting pipeline execution for topic: {topic_id}")
        
        for stage in stages:
            success = await self.execute_stage(stage, job.job_id)
            if not success:
                logger.error(f"[{job.job_id}] Pipeline aborted due to failure in stage: {stage}")
                self.state_manager.update_job_status(job.job_id, PipelineStatus.FAILED)
                return job
                
        logger.info(f"[{job.job_id}] Pipeline execution completed successfully.")
        self.state_manager.update_job_status(job.job_id, PipelineStatus.COMPLETED)
        return job
