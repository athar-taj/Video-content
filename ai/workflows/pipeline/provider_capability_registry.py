import logging
import httpx
import os
from typing import List, Dict
from shared.config.settings import settings

logger = logging.getLogger(__name__)

class ProviderCapabilityRegistry:
    """Detects available environment variables, configuration parameters, and local network status at runtime."""
    
    def __init__(self):
        pass

    async def is_provider_available(self, provider_name: str) -> bool:
        """Checks if a provider is enabled, configured, and reachable."""
        name = provider_name.lower()
        
        # 1. Mock provider is always available for testing/dev
        if name == "mock":
            return True
            
        # 2. Ollama provider has been removed.

        # 3. OpenAI provider
        if name == "openai":
            enabled = getattr(settings, "ENABLE_OPENAI", True)
            key_exists = bool(settings.OPENAI_API_KEY)
            return enabled and key_exists

        # 4. Claude provider
        if name == "claude":
            enabled = getattr(settings, "ENABLE_CLAUDE", True)
            key_exists = bool(os.environ.get("CLAUDE_API_KEY") or os.environ.get("ANTHROPIC_API_KEY"))
            return enabled and key_exists

        # 5. Mistral provider
        if name == "mistral":
            enabled = getattr(settings, "ENABLE_MISTRAL", True) if hasattr(settings, "ENABLE_MISTRAL") else True
            key_exists = bool(settings.MISTRAL_API_KEY)
            return enabled and key_exists

        # 6. Hugging Face provider (local execution checks)
        if name in ("huggingface", "hf"):
            enabled = getattr(settings, "HF_ENABLED", True)
            try:
                import transformers
                import torch
                return enabled
            except ImportError:
                return False

        # 7. Kokoro TTS (Local)
        if name == "kokoro":
            return getattr(settings, "ENABLE_KOKORO", True)

        # 8. Sarvam TTS (Cloud)
        if name == "sarvam":
            enabled = getattr(settings, "ENABLE_SARVAM", True)
            key_exists = bool(settings.SARVAM_API_KEY)
            return enabled and key_exists

        # 9. Murf TTS (Cloud)
        if name == "murf":
            enabled = getattr(settings, "ENABLE_MURF", True)
            # Murf might use ENV keys like MURF_API_KEY
            key_exists = bool(os.environ.get("MURF_API_KEY"))
            return enabled and key_exists

        # 10. ElevenLabs TTS (Cloud)
        if name == "elevenlabs":
            enabled = getattr(settings, "ENABLE_ELEVENLABS", True) if hasattr(settings, "ENABLE_ELEVENLABS") else True
            key_exists = bool(os.environ.get("ELEVENLABS_API_KEY"))
            return enabled and key_exists

        # Unknown provider
        logger.warning(f"Unknown provider '{provider_name}' queried in capability registry.")
        return False

    async def get_healthy_providers(self, category: str) -> List[str]:
        """Returns a list of functional providers for LLM or TTS categories."""
        category = category.lower()
        healthy = []
        
        if category == "llm":
            candidates = ["mock", "openai", "claude", "mistral", "huggingface"]
        elif category == "tts":
            candidates = ["kokoro", "sarvam", "murf", "elevenlabs"]
        else:
            logger.error(f"Unknown capability category: {category}")
            return []

        for candidate in candidates:
            if await self.is_provider_available(candidate):
                # Standardize case to match original preferences (e.g. Ollama, OpenAI)
                standardized = candidate
                if candidate == "openai":
                    standardized = "OpenAI"
                elif candidate == "claude":
                    standardized = "Claude"
                elif candidate == "mistral":
                    standardized = "Mistral"
                elif candidate in ("huggingface", "hf"):
                    standardized = "HuggingFace"
                elif candidate == "kokoro":
                    standardized = "Kokoro"
                elif candidate == "sarvam":
                    standardized = "Sarvam"
                elif candidate == "murf":
                    standardized = "Murf"
                elif candidate == "elevenlabs":
                    standardized = "ElevenLabs"
                elif candidate == "mock":
                    standardized = "Mock"
                healthy.append(standardized)

        return healthy

# Global instance
provider_capability_registry = ProviderCapabilityRegistry()
