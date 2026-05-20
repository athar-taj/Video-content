import httpx
from typing import Dict, Any
from ai.providers.base_provider import BaseLLMProvider, GenerationResponse
from shared.config.settings import settings
from shared.logging.logger import log

class HuggingFaceProvider(BaseLLMProvider):
    """Provider for HuggingFace Inference API."""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or settings.HF_API_TOKEN
        self.base_url = "https://api-inference.huggingface.co/models"

    async def generate(self, prompt: str, **kwargs) -> GenerationResponse:
        model = kwargs.get("model", "mistralai/Mistral-7B-Instruct-v0.2")
        log.debug(f"HuggingFace generating with {model}...")
        
        url = f"{self.base_url}/{model}"
        async with httpx.AsyncClient(timeout=30.0) as client:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": kwargs.get("max_tokens", 500),
                    "temperature": kwargs.get("temperature", 0.7)
                }
            }
            
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            
            # HF returns list of results
            content = data[0]["generated_text"] if isinstance(data, list) else data.get("generated_text", "")
            
            return GenerationResponse(
                content=content,
                provider="huggingface",
                model=model,
                usage={"total_tokens": len(content.split())}, # Estimation
                metadata={}
            )

    async def health_check(self) -> bool:
        return bool(self.api_key)
