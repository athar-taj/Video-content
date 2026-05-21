import logging
from typing import List, Optional
from ai.workflows.memory.provider_health_memory import provider_health_memory
from ai.workflows.pipeline.provider_capability_registry import provider_capability_registry

logger = logging.getLogger(__name__)

class ProviderRouter:
    """Selects and routes requests to healthy LLM and TTS providers based on workflow level."""
    
    def __init__(self):
        from shared.config.settings import settings
        
        # LLM Provider Preference Chains (Base chains, now including specialized workflows)
        self.llm_base_chains = {
            "cheap": ["Ollama", "Mistral", "OpenAI"],
            "balanced": ["Mistral", "OpenAI", "Claude"],
            "premium": ["Claude", "OpenAI", "Mistral", "Ollama"],
            
            # New specialized workflows
            "ultra_cheap_workflow": ["Ollama", "HuggingFace"],
            "local_only_workflow": ["Ollama"],
            "hybrid_workflow": ["Ollama"],
            "premium_optional_workflow": ["Claude", "OpenAI", "Mistral", "Ollama"]
        }
        
        # TTS Provider Preference Chains
        self.tts_base_chains = {
            "cheap": ["Kokoro", "Sarvam", "ElevenLabs"],
            "balanced": ["Sarvam", "Kokoro", "ElevenLabs"],
            "premium": ["ElevenLabs", "Sarvam", "Kokoro"],
            
            # New specialized workflows
            "ultra_cheap_workflow": ["Kokoro"],
            "local_only_workflow": ["Kokoro"],
            "hybrid_workflow": ["Sarvam", "Kokoro"],
            "premium_optional_workflow": ["ElevenLabs", "Sarvam", "Kokoro"]
        }

        # Keep legacy properties for backward compatibility
        self.llm_chains = self.llm_base_chains
        self.tts_chains = self.tts_base_chains

    async def get_llm_chain(self, workflow_type: str) -> List[str]:
        """Dynamically filters the LLM chain by querying provider capabilities and health."""
        base_chain = self.llm_base_chains.get(workflow_type)
        if not base_chain:
            # Fallback to cheap if unknown
            base_chain = self.llm_base_chains.get("cheap", ["Ollama"])
            
        filtered = []
        for provider in base_chain:
            if await provider_capability_registry.is_provider_available(provider):
                if provider_health_memory.is_healthy(provider):
                    filtered.append(provider)
                    
        if not filtered:
            fallback = "Ollama"
            from shared.config.settings import settings
            if settings.ENV == "development":
                if not await provider_capability_registry.is_provider_available("ollama"):
                    fallback = "Mock"
            logger.warning(
                f"⚠️ All LLM providers in chain for '{workflow_type}' are unavailable or unhealthy! "
                f"Falling back to {fallback}."
            )
            return [fallback]
            
        logger.debug(f"Resolved LLM chain for '{workflow_type}': {filtered}")
        return filtered

    async def get_tts_chain(self, workflow_type: str) -> List[str]:
        """Dynamically filters the TTS chain by querying provider capabilities and health."""
        base_chain = self.tts_base_chains.get(workflow_type)
        if not base_chain:
            base_chain = self.tts_base_chains.get("cheap", ["Kokoro"])
            
        filtered = []
        for provider in base_chain:
            if await provider_capability_registry.is_provider_available(provider):
                if provider_health_memory.is_healthy(provider):
                    filtered.append(provider)
                    
        if not filtered:
            logger.warning(
                f"⚠️ All TTS providers in chain for '{workflow_type}' are unavailable or unhealthy! "
                f"Falling back to Kokoro."
            )
            return ["Kokoro"]
            
        logger.debug(f"Resolved TTS chain for '{workflow_type}': {filtered}")
        return filtered

    async def route_llm(self, workflow_type: str) -> str:
        """Route to the best healthy LLM provider for the given workflow level."""
        chain = await self.get_llm_chain(workflow_type)
        logger.info(f"Routed LLM to healthy provider: {chain[0]} (Workflow: {workflow_type})")
        return chain[0]

    async def route_tts(self, workflow_type: str) -> str:
        """Route to the best healthy TTS provider for the given workflow level."""
        chain = await self.get_tts_chain(workflow_type)
        logger.info(f"Routed TTS to healthy provider: {chain[0]} (Workflow: {workflow_type})")
        return chain[0]

    def report_failure(self, provider: str):
        """Report failure to trigger health memory updates."""
        provider_health_memory.record_failure(provider)

    def report_success(self, provider: str):
        """Report success to clear provider failure history."""
        provider_health_memory.record_success(provider)
