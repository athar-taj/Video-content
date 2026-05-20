from typing import Dict, Any
from ai.generation.generation_service import GenerationService
from shared.logging.logger import log

class StoryRewriter:
    """Converts raw Reddit posts into conversational, short-form scripts."""
    
    def __init__(self, service: GenerationService):
        self.service = service

    async def rewrite(self, raw_content: str, target_duration: int = 60, provider: Optional[str] = None) -> str:
        log.debug(f"Rewriting story for {target_duration}s duration...")
        
        # Word count estimate (approx 2.5 words per second)
        target_word_count = target_duration * 2.5
        
        variables = {
            "content": raw_content,
            "target_words": int(target_word_count)
        }
        
        response = await self.service.generate_content(
            task_name="script_generation",
            template_name="short_story_v1",
            variables=variables,
            provider=provider
        )
        
        return response.content.strip()
