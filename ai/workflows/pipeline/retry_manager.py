import logging
import asyncio
from typing import Callable, Any

logger = logging.getLogger(__name__)

class RetryManager:
    """Manages execution retries with exponential backoff."""
    
    def __init__(self, max_retries: int = 3, base_backoff_seconds: int = 2):
        self.max_retries = max_retries
        self.base_backoff = base_backoff_seconds

    async def execute_with_retry(self, stage_name: str, func: Callable, *args, **kwargs) -> Any:
        """Executes an async function with retry logic."""
        retries = 0
        
        while True:
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                retries += 1
                if retries > self.max_retries:
                    logger.error(f"Stage '{stage_name}' failed after {self.max_retries} retries. Error: {str(e)}")
                    raise
                    
                backoff_time = self.base_backoff * (2 ** (retries - 1))
                logger.warning(f"Stage '{stage_name}' failed. Retrying ({retries}/{self.max_retries}) in {backoff_time}s... Error: {str(e)}")
                await asyncio.sleep(backoff_time)
