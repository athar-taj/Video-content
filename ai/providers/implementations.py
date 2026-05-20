import httpx
from typing import Optional, Dict, Any
from ai.providers.base import BaseLLMProvider
from shared.config.settings import settings
from shared.logging.logger import log

class OllamaProvider(BaseLLMProvider):
    def __init__(self):
        self.base_url = f"{settings.OLLAMA_BASE_URL}/api"
        self.default_model = settings.DEFAULT_LOCAL_MODEL

    async def generate(
        self, 
        prompt: str, 
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> str:
        payload = {
            "model": model or self.default_model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                resp = await client.post(f"{self.base_url}/generate", json=payload)
                resp.raise_for_status()
                return resp.json().get("response", "")
            except Exception as e:
                log.error(f"Ollama generation failed: {e}")
                return ""

    async def health_check(self) -> bool:
        async with httpx.AsyncClient(timeout=5.0) as client:
            try:
                resp = await client.get(f"{settings.OLLAMA_BASE_URL}/")
                return resp.status_code == 200
            except:
                return False

    async def get_token_usage(self) -> Dict[str, int]:
        return {"tokens": 0}

class MistralProvider(BaseLLMProvider):
    def __init__(self):
        self.api_key = settings.MISTRAL_API_KEY
        self.base_url = "https://api.mistral.ai/v1/chat/completions"

    async def generate(
        self, 
        prompt: str, 
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> str:
        if not self.api_key:
            log.warning("Mistral API key not set. Skipping.")
            return ""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model or "mistral-tiny",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                resp = await client.post(self.base_url, headers=headers, json=payload)
                resp.raise_for_status()
                data = resp.json()
                return data["choices"][0]["message"]["content"]
            except Exception as e:
                log.error(f"Mistral generation failed: {e}")
                return ""

    async def health_check(self) -> bool:
        return bool(self.api_key)

    async def get_token_usage(self) -> Dict[str, int]:
        return {"tokens": 0}

class HuggingFaceProvider(BaseLLMProvider):
    def __init__(self):
        self.token = settings.HF_API_TOKEN
        self.base_url = "https://api-inference.huggingface.co/models/"

    async def generate(
        self, 
        prompt: str, 
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> str:
        if not self.token:
            return ""
        
        model_id = model or "mistralai/Mistral-7B-Instruct-v0.2"
        headers = {"Authorization": f"Bearer {self.token}"}
        payload = {"inputs": prompt, "parameters": {"temperature": temperature, "max_new_tokens": max_tokens}}

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                resp = await client.post(f"{self.base_url}{model_id}", headers=headers, json=payload)
                resp.raise_for_status()
                data = resp.json()
                return data[0].get("generated_text", "") if isinstance(data, list) else ""
            except Exception as e:
                log.error(f"HF generation failed: {e}")
                return ""

    async def health_check(self) -> bool:
        return bool(self.token)

    async def get_token_usage(self) -> Dict[str, int]:
        return {"tokens": 0}
