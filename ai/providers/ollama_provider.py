import httpx
from typing import Dict, Any
from ai.providers.base_provider import BaseLLMProvider, GenerationResponse
from shared.config.settings import settings
from shared.logging.logger import log

class OllamaProvider(BaseLLMProvider):
    """Provider for local Ollama instance."""
    
    def __init__(self, base_url: str = None):
        self.base_url = base_url or settings.OLLAMA_BASE_URL
        self.url = f"{self.base_url}/api/chat"

    async def generate(self, prompt: str, **kwargs) -> GenerationResponse:
        model = kwargs.get("model")
        if not model:
            from ai.providers.local_model_manager import local_model_manager
            model = local_model_manager.recommend_local_model()
            # Verify and pull model in the background if missing
            await local_model_manager.verify_and_preload_model(model)
            
        log.debug(f"Ollama generating with {model}...")
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            payload = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
                "options": {
                    "temperature": kwargs.get("temperature", 0.7)
                }
            }
            
            response = await client.post(self.url, json=payload)
            response.raise_for_status()
            data = response.json()
            
            return GenerationResponse(
                content=data["message"]["content"],
                provider="ollama",
                model=model,
                usage={
                    "prompt_tokens": data.get("prompt_eval_count", 0),
                    "completion_tokens": data.get("eval_count", 0),
                    "total_tokens": data.get("prompt_eval_count", 0) + data.get("eval_count", 0)
                },
                metadata={}
            )

    async def health_check(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                resp = await client.get(f"{self.base_url}/api/tags")
                return resp.status_code == 200
        except Exception:
            return False
