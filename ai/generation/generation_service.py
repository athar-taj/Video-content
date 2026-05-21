import time
from typing import Dict, Any, Optional
from ai.providers.factory import ProviderRouter, ProviderFactory
from ai.generation.prompt_engine import PromptEngine
from ai.providers.base_provider import GenerationResponse
from shared.logging.logger import log
from shared.config.settings import settings

class GenerationService:
    """Master service for AI content generation."""
    
    @staticmethod
    async def generate_content(
        task_name: str, 
        template_name: str, 
        variables: Dict[str, Any],
        **kwargs
    ) -> GenerationResponse:
        """High-level method to generate AI content for a specific task."""
        
        # 1. Select Provider & Model
        provider_name = kwargs.pop("provider", None)
        if provider_name:
            provider = ProviderFactory.get_provider(provider_name)
        else:
            provider = await ProviderRouter.get_provider_for_task(task_name)
        
        # 2. Load Prompt
        category = task_name.split("_")[0] + "s" # e.g. hook_generation -> hooks
        template_path = PromptEngine.get_template_path(category, template_name)
        prompt = PromptEngine.load_prompt(template_path, variables)
        
        # Optimize prompt for local models
        is_local = provider.__class__.__name__ in ["OllamaProvider", "HuggingFaceProvider"]
        if is_local:
            prompt = PromptEngine.optimize_for_local_model(prompt, task_name)
            log.debug(f"Optimized prompt for local model {provider.__class__.__name__}")
        
        # 3. Generate
        start_time = time.time()
        try:
            response = await provider.generate(prompt, **kwargs)
            duration = time.time() - start_time
            
            log.info(f"✨ Generated {task_name} using {response.provider}/{response.model} in {duration:.2f}s")
            
            # 4. Add duration to metadata
            response.metadata["duration"] = duration
            return response
            
        except Exception as e:
            log.error(f"Generation failed for task {task_name}: {e}")
            raise
