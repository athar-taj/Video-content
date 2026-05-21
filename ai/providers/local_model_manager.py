import httpx
import logging
from typing import List, Dict, Any
from shared.config.settings import settings

logger = logging.getLogger(__name__)

class LocalModelManager:
    """Manages local model sizes, recommendations based on hardware resource constraints, and preloading status."""
    
    def __init__(self):
        self.ollama_base_url = settings.OLLAMA_BASE_URL

    def recommend_local_model(self, task: str = "general") -> str:
        """Recommends an appropriate model size based on MAX_VRAM_GB and LOCAL_MODEL_SIZE."""
        size_pref = getattr(settings, "LOCAL_MODEL_SIZE", "auto").lower()
        vram = getattr(settings, "MAX_VRAM_GB", 8.0)
        
        # Determine size tier
        if size_pref in ["small", "medium", "large"]:
            tier = size_pref
        else:
            # Auto-detect based on VRAM
            if vram < 4.0:
                tier = "small"
            elif vram < 12.0:
                tier = "medium"
            else:
                tier = "large"
                
        # Select model based on tier and task
        if tier == "small":
            return "qwen2.5:1.5b"
        elif tier == "medium":
            # For general tasks or script generation, default to qwen2.5:7b
            return "qwen2.5:7b"
        else:
            # Large tier
            return "qwen2.5:14b"

    async def get_installed_models(self) -> List[str]:
        """Queries local Ollama instance for pulled models."""
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                resp = await client.get(f"{self.ollama_base_url}/api/tags")
                if resp.status_code == 200:
                    data = resp.json()
                    models = data.get("models", [])
                    return [m.get("name") for m in models if "name" in m]
        except Exception as e:
            logger.warning(f"Failed to query installed Ollama models: {e}")
        return []

    async def verify_and_preload_model(self, model_name: str) -> bool:
        """Checks if a model is installed, and warns / triggers a pull if missing."""
        installed = await self.get_installed_models()
        
        # Try both exact match and suffix/prefix match
        match_found = False
        normalized_target = model_name.lower()
        
        for name in installed:
            norm_name = name.lower()
            if normalized_target == norm_name:
                match_found = True
                break
            # e.g., if target is 'qwen2.5:7b' and norm_name is 'qwen2.5:7b-instruct' or similar
            if normalized_target in norm_name or norm_name in normalized_target:
                match_found = True
                break
                
        if match_found:
            logger.info(f"Local model '{model_name}' is verified and installed.")
            return True
            
        logger.warning(
            f"⚠️ Local model '{model_name}' was not found in Ollama! "
            f"Please run `ollama pull {model_name}` to avoid execution failures."
        )
        
        # Optionally attempt to trigger a non-blocking pull
        try:
            logger.info(f"Attempting to initiate background pull for '{model_name}'...")
            # We run it with a very short timeout and ignore errors, because a full pull blocks the response
            # unless we stream or do it in the background.
            async with httpx.AsyncClient(timeout=1.0) as client:
                await client.post(f"{self.ollama_base_url}/api/pull", json={"name": model_name, "stream": False})
        except httpx.TimeoutException:
            # This is expected since we set timeout to 1.0s and pull takes longer
            logger.info(f"Ollama pull request for '{model_name}' submitted successfully in background.")
            return True
        except Exception as e:
            logger.error(f"Failed to initiate background pull for model '{model_name}': {e}")
            
        return False

# Global instance
local_model_manager = LocalModelManager()
