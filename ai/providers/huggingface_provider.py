import time
import httpx
import logging
from typing import Dict, Any, Optional
from ai.providers.base_provider import BaseLLMProvider, GenerationResponse
from shared.config.settings import settings

logger = logging.getLogger(__name__)

class HuggingFaceProvider(BaseLLMProvider):
    """
    Provider for local Hugging Face (Transformers and GGUF) model execution,
    with automatic hardware routing and fallback capabilities.
    """
    
    def __init__(self):
        # We also keep the token/URL configs for cloud/SaaS fallback capability
        self.token = settings.HF_API_TOKEN
        self.base_url = "https://api-inference.huggingface.co/models/"

    async def generate(self, prompt: str, **kwargs) -> GenerationResponse:
        model_id = kwargs.get("model")
        temperature = kwargs.get("temperature", 0.7)
        max_tokens = kwargs.get("max_tokens", settings.HF_MAX_NEW_TOKENS)
        workflow_type = kwargs.get("workflow_type", "cheap")
        
        from ai.providers.local_model_manager import local_model_manager
        
        # Determine model
        if not model_id:
            model_id = local_model_manager.recommend_model(workflow_type)
            
        logger.info(f"[HF_LOCAL] Generating with model '{model_id}'...")
        start_time = time.time()
        
        try:
            # 1. Attempt local model generation
            response = await self._generate_local(model_id, prompt, temperature, max_tokens)
            duration = time.time() - start_time
            logger.info(f"✨ Local generation with '{model_id}' succeeded in {duration:.2f}s.")
            return response
            
        except Exception as local_err:
            logger.warning(
                f"⚠️ Local generation with model '{model_id}' failed: {local_err}. "
                f"Checking fallback configurations..."
            )
            
            # 2. Fallback execution
            if getattr(settings, "HF_ENABLE_FALLBACKS", True):
                fallback_response = await self._execute_fallback(prompt, model_id, local_err, **kwargs)
                if fallback_response:
                    return fallback_response
            
            # If fallbacks fail or are disabled, raise the original exception
            logger.critical(f"❌ Both local execution and all fallbacks failed for model '{model_id}'!")
            raise local_err

    async def _generate_local(self, model_id: str, prompt: str, temperature: float, max_tokens: int) -> GenerationResponse:
        """Loads and executes model locally."""
        from ai.providers.local_model_manager import local_model_manager
        
        # Load model and tokenizer
        model, tokenizer = local_model_manager.load_model(model_id)
        
        # Check if it is a GGUF model (Llama instance from llama-cpp-python)
        is_gguf = tokenizer is None
        
        if is_gguf:
            # GGUF runtime execution
            import asyncio
            
            def _gguf_sync():
                # Llama.create_completion is a blocking synchronous call, run in executor
                res = model.create_completion(
                    prompt=prompt,
                    max_tokens=max_tokens,
                    temperature=temperature,
                )
                return res
                
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, _gguf_sync)
            
            text = result["choices"][0]["text"]
            usage = result.get("usage", {
                "prompt_tokens": len(prompt.split()),  # fallback estimation
                "completion_tokens": len(text.split()),
                "total_tokens": len(prompt.split()) + len(text.split())
            })
            
            return GenerationResponse(
                content=text,
                provider="huggingface_local_gguf",
                model=model_id,
                usage={
                    "prompt_tokens": usage.get("prompt_tokens", 0),
                    "completion_tokens": usage.get("completion_tokens", 0),
                    "total_tokens": usage.get("total_tokens", 0)
                },
                metadata={"device": local_model_manager.device, "backend": "llama-cpp-python"}
            )
        else:
            # Standard Hugging Face PyTorch/Transformers execution
            import torch
            import asyncio
            
            # Run tokenizer and placement on device
            inputs = tokenizer(prompt, return_tensors="pt")
            if local_model_manager.device == "cuda":
                inputs = {k: v.cuda() for k, v in inputs.items()}
                
            input_len = inputs["input_ids"].shape[1]
            
            def _transformers_sync():
                # Disable gradient calculation for faster inference
                with torch.no_grad():
                    outputs = model.generate(
                        **inputs,
                        max_new_tokens=max_tokens,
                        temperature=temperature,
                        do_sample=temperature > 0.0,
                        pad_token_id=tokenizer.pad_token_id,
                        eos_token_id=tokenizer.eos_token_id
                    )
                return outputs
                
            loop = asyncio.get_event_loop()
            outputs = await loop.run_in_executor(None, _transformers_sync)
            
            # Slice output to decode only the newly generated tokens
            generated_tokens = outputs[0][input_len:]
            text = tokenizer.decode(generated_tokens, skip_special_tokens=True)
            
            usage = {
                "prompt_tokens": input_len,
                "completion_tokens": len(generated_tokens),
                "total_tokens": input_len + len(generated_tokens)
            }
            
            return GenerationResponse(
                content=text,
                provider="huggingface_local_transformers",
                model=model_id,
                usage=usage,
                metadata={"device": local_model_manager.device, "backend": "pytorch"}
            )

    async def _execute_fallback(self, prompt: str, model_id: str, original_error: Exception, **kwargs) -> Optional[GenerationResponse]:
        """Falls back to remote APIs (OpenRouter, OpenAI, or Hugging Face Inference API)."""
        logger.info("[HF_FALLBACK] Initiating cloud fallback routing...")
        
        # 1. Fallback option A: OpenAI API (via gpt-4o-mini if api key exists)
        if settings.OPENAI_API_KEY:
            try:
                logger.info("[HF_FALLBACK] Routing to OpenAI (gpt-4o-mini)...")
                from ai.providers.openai_provider import OpenAIProvider
                openai_p = OpenAIProvider()
                return await openai_p.generate(prompt, model="gpt-4o-mini", **kwargs)
            except Exception as e:
                logger.warning(f"[HF_FALLBACK] OpenAI fallback failed: {e}")
                
        # 2. Fallback option B: Hugging Face SaaS Inference API (if HF Token exists)
        if self.token:
            try:
                # Use standard repo id or map to a stable cloud endpoints
                cloud_model = "mistralai/Mistral-7B-Instruct-v0.2"
                logger.info(f"[HF_FALLBACK] Routing to Hugging Face Inference API ({cloud_model})...")
                
                headers = {"Authorization": f"Bearer {self.token}"}
                payload = {
                    "inputs": prompt,
                    "parameters": {
                        "temperature": kwargs.get("temperature", 0.7),
                        "max_new_tokens": kwargs.get("max_tokens", 512)
                    }
                }
                
                async with httpx.AsyncClient(timeout=30.0) as client:
                    resp = await client.post(f"{self.base_url}{cloud_model}", headers=headers, json=payload)
                    resp.raise_for_status()
                    data = resp.json()
                    
                    content = ""
                    if isinstance(data, list) and len(data) > 0:
                        content = data[0].get("generated_text", "")
                    elif isinstance(data, dict):
                        content = data.get("generated_text", "")
                        
                    # Remove prompt prefix if SaaS returns it
                    if content.startswith(prompt):
                        content = content[len(prompt):]
                        
                    return GenerationResponse(
                        content=content.strip(),
                        provider="huggingface_api",
                        model=cloud_model,
                        usage={"prompt_tokens": len(prompt.split()), "completion_tokens": len(content.split()), "total_tokens": len(prompt.split()) + len(content.split())},
                        metadata={"type": "cloud_fallback"}
                    )
            except Exception as e:
                logger.warning(f"[HF_FALLBACK] HuggingFace SaaS API fallback failed: {e}")
                
        # 3. Fallback option C: Mock LLM Provider (for local development resiliency)
        if settings.ENV == "development":
            try:
                logger.info("[HF_FALLBACK] Routing to Mock LLM Provider...")
                from ai.providers.mock_provider import MockLLMProvider
                mock_p = MockLLMProvider()
                return await mock_p.generate(prompt, **kwargs)
            except Exception as e:
                logger.warning(f"[HF_FALLBACK] Mock provider fallback failed: {e}")
                
        return None

    async def health_check(self) -> bool:
        """Checks if local Hugging Face runner is healthy."""
        # Returns true if transformers package is installed and importable
        try:
            import transformers
            import torch
            return True
        except ImportError:
            return False
