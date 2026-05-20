from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pydantic import BaseModel

class GenerationResponse(BaseModel):
    content: str
    provider: str
    model: str
    usage: Dict[str, int] # prompt_tokens, completion_tokens, total_tokens
    metadata: Dict[str, Any] = {}

class BaseLLMProvider(ABC):
    """Abstract base class for all LLM providers."""
    
    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> GenerationResponse:
        """Execute a text generation request."""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the provider is healthy and reachable."""
        pass

    def count_tokens(self, text: str) -> int:
        """Rough token estimation (can be overridden by specific providers)."""
        return len(text.split()) # Basic fallback
