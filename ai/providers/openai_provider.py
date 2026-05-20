import httpx
from typing import Dict, Any
from ai.providers.base_provider import BaseLLMProvider, GenerationResponse
from shared.config.settings import settings
from shared.logging.logger import log

class OpenAIProvider(BaseLLMProvider):
    """Provider for OpenAI API."""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or settings.HF_API_TOKEN # Wait, I should add OPENAI_API_KEY to settings
        # Actually I'll use the environment variable directly or from settings if I update it
        self.url = "https://api.openai.com/v1/chat/completions"

    async def generate(self, prompt: str, **kwargs) -> GenerationResponse:
        model = kwargs.get("model", "gpt-4o-mini")
        log.debug(f"OpenAI generating with {model}...")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": kwargs.get("temperature", 0.7),
                "max_tokens": kwargs.get("max_tokens", 1000)
            }
            
            response = await client.post(self.url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            
            return GenerationResponse(
                content=data["choices"][0]["message"]["content"],
                provider="openai",
                model=model,
                usage=data["usage"],
                metadata={"id": data["id"]}
            )

    async def health_check(self) -> bool:
        return bool(self.api_key)
