import logging
from typing import Dict, Any, Optional
from .models import ExecutionContext

logger = logging.getLogger(__name__)

class ContextManager:
    """Manages the shared execution context for a pipeline job."""
    
    def __init__(self):
        # Simple in-memory dict for local dev. In prod, this would likely hit Redis.
        self._contexts: Dict[str, ExecutionContext] = {}

    def create_context(self, job_id: str, initial_data: Optional[Dict[str, Any]] = None) -> ExecutionContext:
        """Create a new context for a job."""
        logger.info(f"Creating execution context for job: {job_id}")
        context = ExecutionContext(job_id=job_id)
        if initial_data:
            context.topic_data = initial_data
        self._contexts[job_id] = context
        return context

    def get_context(self, job_id: str) -> Optional[ExecutionContext]:
        """Retrieve existing context."""
        return self._contexts.get(job_id)

    def update_context(self, job_id: str, updates: Dict[str, Any]) -> ExecutionContext:
        """Update context properties."""
        context = self._contexts.get(job_id)
        if not context:
            logger.warning(f"Attempted to update non-existent context: {job_id}")
            context = self.create_context(job_id)
            
        for key, value in updates.items():
            if hasattr(context, key):
                setattr(context, key, value)
            else:
                context.metadata[key] = value
                
        return context
