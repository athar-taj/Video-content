import logging
from typing import Callable, Dict, Any
from .models import ExecutionContext

logger = logging.getLogger(__name__)

class WorkflowRegistry:
    """Registers and provides pipeline stage handlers."""
    
    def __init__(self):
        self._handlers: Dict[str, Callable] = {}

    def register_stage(self, stage_name: str, handler: Callable):
        """Register an async function to handle a specific stage."""
        logger.info(f"Registering handler for stage: {stage_name}")
        self._handlers[stage_name] = handler

    def get_handler(self, stage_name: str) -> Callable:
        """Retrieve the handler for a stage."""
        handler = self._handlers.get(stage_name)
        if not handler:
            raise ValueError(f"No handler registered for stage: {stage_name}")
        return handler
