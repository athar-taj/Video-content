import time
from typing import Dict, Any, Optional
from ai.generation.generation_service import GenerationService
from ai.generation.script_generator.hook_generator import HookGenerator
from ai.generation.script_generator.story_rewriter import StoryRewriter
from ai.generation.script_generator.duration_controller import DurationController
from ai.generation.script_generator.models import ScriptGenerationResult
from shared.logging.logger import log

class ScriptGenerator:
    """Main orchestrator for the multi-stage script generation pipeline."""
    
    def __init__(self):
        self.service = GenerationService()
        self.hook_gen = HookGenerator(self.service)
        self.story_gen = StoryRewriter(self.service)

    async def generate_full_script(
        self, 
        topic_id: int,
        title: str, 
        raw_body: str, 
        subreddit: str,
        target_duration: int = 60,
        provider: Optional[str] = None
    ) -> ScriptGenerationResult:
        """Runs the end-to-end script generation flow."""
        start_time = time.time()
        log.info(f"🎭 Starting script generation for topic {topic_id}: {title[:30]}...")
        
        try:
            # 1. Generate Hook
            hook = await self.hook_gen.generate_hook(title, subreddit, provider=provider)
            
            # 2. Rewrite Story
            rewritten_story = await self.story_gen.rewrite(raw_body, target_duration, provider=provider)
            
            # 3. Final Assembly
            full_script = f"{hook}\n\n{rewritten_story}"
            
            # 4. Estimation
            est_duration = DurationController.estimate_duration(full_script)
            
            log.info(f"✅ Script generated: {int(est_duration)}s estimate.")
            
            return ScriptGenerationResult(
                topic_id=topic_id,
                hook=hook,
                full_script=full_script,
                duration_target=target_duration,
                provider="multi-stage",
                model="orchestrated",
                metadata={
                    "estimated_duration": est_duration,
                    "generation_time": time.time() - start_time
                }
            )
            
        except Exception as e:
            log.error(f"Script generation flow failed: {e}")
            raise
        
