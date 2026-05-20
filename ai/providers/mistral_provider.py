import httpx
from typing import Dict, Any
from ai.providers.base_provider import BaseLLMProvider, GenerationResponse
from shared.config.settings import settings
from shared.logging.logger import log

class MistralProvider(BaseLLMProvider):
    """Provider for Mistral AI API."""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or settings.MISTRAL_API_KEY
        self.url = "https://api.mistral.ai/v1/chat/completions"

    async def generate(self, prompt: str, **kwargs) -> GenerationResponse:
        model = kwargs.get("model", "mistral-tiny")
        log.debug(f"Mistral generating with {model}...")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": kwargs.get("temperature", 0.7)
            }
            
            response = await client.post(self.url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            
            return GenerationResponse(
                content=data["choices"][0]["message"]["content"],
                provider="mistral",
                model=model,
                usage=data.get("usage", {"total_tokens": 0}),
                metadata={}
            )

    async def health_check(self) -> bool:
        return bool(self.api_key)
