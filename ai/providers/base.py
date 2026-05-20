from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List

class BaseLLMProvider(ABC):
    """Base interface for all LLM providers."""
    
    @abstractmethod
    async def generate(
        self, 
        prompt: str, 
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> str:
        """Generate text from a prompt."""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Verify provider availability."""
        pass

    @abstractmethod
    async def get_token_usage(self) -> Dict[str, int]:
        """Return token usage stats."""
        pass
