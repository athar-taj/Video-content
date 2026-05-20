import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class ProviderHealthMemory:
    """Tracks the health status and failure counts of AI providers (LLM/TTS)."""
    
    def __init__(self, failure_threshold: int = 3, cooldown_minutes: int = 5):
        self.failure_threshold = failure_threshold
        self.cooldown_minutes = cooldown_minutes
        self._failures: Dict[str, int] = {}
        self._disabled_until: Dict[str, datetime] = {}

    def record_failure(self, provider: str):
        """Record a failure for a given provider."""
        self._failures[provider] = self._failures.get(provider, 0) + 1
        logger.warning(f"Recorded failure for provider '{provider}'. Total failures: {self._failures[provider]}")
        
        if self._failures[provider] >= self.failure_threshold:
            disable_time = datetime.utcnow() + timedelta(minutes=self.cooldown_minutes)
            self._disabled_until[provider] = disable_time
            logger.error(f"Provider '{provider}' has exceeded failure threshold. Disabling until {disable_time.isoformat()}")

    def record_success(self, provider: str):
        """Record a success, resetting failure tracking."""
        if provider in self._failures:
            del self._failures[provider]
        if provider in self._disabled_until:
            del self._disabled_until[provider]
            logger.info(f"Provider '{provider}' recovered and is now enabled.")

    def is_healthy(self, provider: str) -> bool:
        """Check if a provider is healthy and not currently disabled."""
        if provider in self._disabled_until:
            if datetime.utcnow() > self._disabled_until[provider]:
                # Cooldown expired, check again/enable
                del self._disabled_until[provider]
                self._failures[provider] = 0
                return True
            return False
        return True

    def get_status(self, provider: str) -> Dict[str, Any]:
        """Get the current health status details of a provider."""
        healthy = self.is_healthy(provider)
        disabled_until = self._disabled_until.get(provider)
        return {
            "provider": provider,
            "healthy": healthy,
            "failures": self._failures.get(provider, 0),
            "disabled_until": disabled_until.isoformat() if disabled_until else None
        }

# Global singleton health memory
provider_health_memory = ProviderHealthMemory()
