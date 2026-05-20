import os
import uuid
import time
from typing import Dict, Any, Optional
from ai.voice.providers.factory import TTSProviderRouter
from ai.voice.providers.base_tts_provider import TTSResponse
from shared.logging.logger import log

class TTSService:
    """Master service for voice generation workflows."""
    
    def __init__(self, output_dir: str = "assets/audio/generated"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    async def generate_narration(
        self, 
        script_text: str, 
        voice_id: str = "af_bella", 
        task_type: str = "default",
        provider: Optional[str] = None
    ) -> TTSResponse:
        """Generates narration for a given script."""
        
        # 1. Select Provider
        if provider:
            from ai.voice.providers.factory import TTSProviderFactory
            provider_inst = TTSProviderFactory.get_provider(provider)
        else:
            provider_inst = await TTSProviderRouter.get_provider_for_task(task_type)
        
        # 2. Prepare Path
        filename = f"{uuid.uuid4()}.mp3"
        output_path = os.path.join(self.output_dir, filename)
        
        # 3. Generate
        start_time = time.time()
        try:
            response = await provider_inst.generate_audio(script_text, voice_id, output_path)
            
            # 4. Add execution metadata
            response.metadata["total_execution_time"] = time.time() - start_time
            log.info(f"🎙️ Narration generated: {response.audio_path} ({response.duration_sec:.2f}s)")
            
            return response
            
        except Exception as e:
            log.error(f"TTS generation failed: {e}")
            raise
