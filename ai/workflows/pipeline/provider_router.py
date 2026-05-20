import logging
from typing import List, Optional
from ai.workflows.memory.provider_health_memory import provider_health_memory

logger = logging.getLogger(__name__)

class ProviderRouter:
    """Selects and routes requests to healthy LLM and TTS providers based on workflow level."""
    
    def __init__(self):
        from shared.config.settings import settings
        # LLM Provider Preference Chains
        if settings.ENV == "development":
            self.llm_chains = {
                "cheap": ["Mock", "Ollama", "Mistral", "OpenAI"],
                "balanced": ["Mock", "Mistral", "OpenAI", "Claude"],
                "premium": ["Mock", "Claude", "OpenAI", "Mistral"]
            }
        else:
            self.llm_chains = {
                "cheap": ["Ollama", "Mistral", "OpenAI"],
                "balanced": ["Mistral", "OpenAI", "Claude"],
                "premium": ["Claude", "OpenAI", "Mistral"]
            }
        
        # TTS Provider Preference Chains
        self.tts_chains = {
            "cheap": ["Kokoro", "Sarvam", "ElevenLabs"],
            "balanced": ["Sarvam", "Kokoro", "ElevenLabs"],
            "premium": ["ElevenLabs", "Sarvam", "Kokoro"]
        }

    def route_llm(self, workflow_type: str) -> str:
        """Route to the best healthy LLM provider for the given workflow level."""
        chain = self.llm_chains.get(workflow_type, self.llm_chains["cheap"])
        for provider in chain:
            if provider_health_memory.is_healthy(provider):
                logger.info(f"Routed LLM to healthy provider: {provider} (Workflow: {workflow_type})")
                return provider
        
        # Fallback to absolute default if everything in chain is disabled
        logger.warning(f"All preferred LLM providers unhealthy for {workflow_type}! Falling back to Ollama.")
        return "Ollama"

    def route_tts(self, workflow_type: str) -> str:
        """Route to the best healthy TTS provider for the given workflow level."""
        chain = self.tts_chains.get(workflow_type, self.tts_chains["cheap"])
        for provider in chain:
            if provider_health_memory.is_healthy(provider):
                logger.info(f"Routed TTS to healthy provider: {provider} (Workflow: {workflow_type})")
                return provider
        
        # Fallback to absolute default if everything in chain is disabled
        logger.warning(f"All preferred TTS providers unhealthy for {workflow_type}! Falling back to Kokoro.")
        return "Kokoro"

    def report_failure(self, provider: str):
        """Report failure to trigger health memory updates."""
        provider_health_memory.record_failure(provider)

    def report_success(self, provider: str):
        """Report success to clear provider failure history."""
        provider_health_memory.record_success(provider)
