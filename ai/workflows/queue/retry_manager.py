import math
import logging
from typing import Dict, Any, Tuple, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class RetryManager:
    """Manages job retries, calculates backoffs, and decides on provider fallbacks."""

    def should_retry(self, current_retry_count: int, max_retries: int) -> bool:
        """Determines if a job should be retried based on limits."""
        return current_retry_count < max_retries

    def calculate_backoff(self, retry_count: int, base_delay: float = 2.0, max_delay: float = 300.0) -> float:
        """Calculates exponential backoff delay with jitter.
        Formula: base_delay * (2 ^ retry_count)
        """
        delay = base_delay * math.pow(2, retry_count)
        # Apply maximum limit
        delay = min(delay, max_delay)
        return delay

    def get_fallback_provider(self, job_type: str, failed_provider: str, workflow_type: str = "cheap") -> Optional[str]:
        """Provides fallback routing for failed external API providers.
        For example:
        If Kokoro fails during TTS, fallback to OpenAI.
        If OpenAI script generation fails, fallback to Ollama (Mistral).
        """
        fallback_maps = {
            "tts": {
                "kokoro": "openai",
                "sarvam": "kokoro"
            },
            "script": {
                "openai": "mistral",
                "mistral": "huggingface"
            }
        }
        
        provider_map = fallback_maps.get(job_type.lower())
        if provider_map:
            return provider_map.get(failed_provider.lower())
            
        return None

# Singleton instance
retry_manager = RetryManager()
