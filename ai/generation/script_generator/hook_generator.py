from typing import Dict, Any
from ai.generation.generation_service import GenerationService
from shared.logging.logger import log

class HookGenerator:
    """Generates viral hooks for short-form scripts."""
    
    def __init__(self, service: GenerationService):
        self.service = service

    async def generate_hook(self, topic: str, subreddit: str, style: str = "suspense", provider: Optional[str] = None) -> str:
        log.debug(f"Generating {style} hook for: {topic[:30]}...")
        
        variables = {
            "topic": topic,
            "subreddit": subreddit,
            "style": style,
            "tone": style # Mapping for template
        }
        
        response = await self.service.generate_content(
            task_name="hook_generation",
            template_name="viral_hook_v1",
            variables=variables,
            provider=provider
        )
        
        return response.content.strip()
