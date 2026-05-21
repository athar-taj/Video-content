from typing import Dict, Any
from ai.providers.base_provider import BaseLLMProvider
from ai.providers.openai_provider import OpenAIProvider
from ai.providers.mistral_provider import MistralProvider
from ai.providers.ollama_provider import OllamaProvider
from ai.providers.huggingface_provider import HuggingFaceProvider
from shared.config.settings import settings

class ProviderFactory:
    """Factory to manage and retrieve provider instances."""
    
    _instances: Dict[str, BaseLLMProvider] = {}

    @classmethod
    def get_provider(cls, name: str) -> BaseLLMProvider:
        name = name.lower()
        if name not in cls._instances:
            if name == "openai":
                cls._instances[name] = OpenAIProvider()
            elif name == "mistral":
                cls._instances[name] = MistralProvider()
            elif name == "ollama":
                cls._instances[name] = OllamaProvider()
            elif name == "huggingface":
                cls._instances[name] = HuggingFaceProvider()
            elif name == "mock":
                from ai.providers.mock_provider import MockLLMProvider
                cls._instances[name] = MockLLMProvider()
            else:
                raise ValueError(f"Unknown provider: {name}")
        return cls._instances[name]

class ProviderRouter:
    """Task-based router to select the best provider and model."""
    
    @staticmethod
    async def get_provider_for_task(task_name: str) -> BaseLLMProvider:
        from ai.workflows.pipeline.provider_capability_registry import provider_capability_registry
        from shared.logging.logger import log
        
        # 1. Get preferred provider from settings
        preferred_name = settings.MODEL_ROUTING.get(task_name, "ollama")
        
        # 2. Capability and health check with fallback
        if await provider_capability_registry.is_provider_available(preferred_name):
            provider = ProviderFactory.get_provider(preferred_name)
            if await provider.health_check():
                return provider
            
        # 3. Automatic fallback to Ollama (local) if primary is down/unavailable
        if preferred_name.lower() != "ollama":
            log.warning(f"Preferred provider '{preferred_name}' for task '{task_name}' is down or unavailable. Falling back to Ollama.")
            return ProviderFactory.get_provider("ollama")
            
        return ProviderFactory.get_provider("ollama")
