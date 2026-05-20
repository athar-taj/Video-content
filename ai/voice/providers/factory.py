from typing import Dict
from ai.voice.providers.base_tts_provider import BaseTTSProvider
from ai.voice.providers.kokoro_provider import KokoroProvider
from ai.voice.providers.sarvam_provider import SarvamProvider
from shared.config.settings import settings

class TTSProviderFactory:
    """Factory for managing TTS provider instances."""
    
    _instances: Dict[str, BaseTTSProvider] = {}

    @classmethod
    def get_provider(cls, name: str) -> BaseTTSProvider:
        name = name.lower()
        if name not in cls._instances:
            if name == "kokoro":
                cls._instances[name] = KokoroProvider()
            elif name == "sarvam":
                cls._instances[name] = SarvamProvider()
            else:
                # Fallback to Kokoro for testing
                return KokoroProvider()
        return cls._instances[name]

class TTSProviderRouter:
    """Routes TTS requests based on task type and health."""
    
    @staticmethod
    async def get_provider_for_task(task_type: str = "default") -> BaseTTSProvider:
        preferred = settings.DEFAULT_LOCAL_MODEL if task_type == "default" else "sarvam"
        
        # Simple routing logic
        if task_type == "premium":
            provider = TTSProviderFactory.get_provider("sarvam")
        else:
            provider = TTSProviderFactory.get_provider("kokoro")
            
        if await provider.health_check():
            return provider
            
        return TTSProviderFactory.get_provider("kokoro")
