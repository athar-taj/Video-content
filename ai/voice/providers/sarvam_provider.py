import httpx
import os
from typing import List, Dict, Any
from ai.voice.providers.base_tts_provider import BaseTTSProvider, TTSResponse
from shared.config.settings import settings
from shared.logging.logger import log

class SarvamProvider(BaseTTSProvider):
    """Sarvam AI TTS provider."""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or settings.SARVAM_API_KEY
        self.url = "https://api.sarvam.ai/text-to-speech"

    async def generate_audio(self, text: str, voice_id: str, output_path: str, **kwargs) -> TTSResponse:
        log.info(f"Sarvam AI generating audio with voice {voice_id}...")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            headers = {"api-subscription-key": self.api_key}
            payload = {
                "inputs": [text],
                "target_language_code": "en-IN",
                "speaker": voice_id,
                "model": "bullet_v1"
            }
            
            # This is a representative implementation of Sarvam's API
            # Note: Actual response handling depends on Sarvam's exact schema
            response = await client.post(self.url, headers=headers, json=payload)
            response.raise_for_status()
            
            with open(output_path, "wb") as f:
                f.write(response.content)
                
            return TTSResponse(
                audio_path=output_path,
                provider="sarvam",
                voice=voice_id,
                duration_sec=0.0, # Will be calculated by audio_processor
                file_size_bytes=os.path.getsize(output_path),
                metadata={}
            )

    async def get_available_voices(self) -> List[Dict[str, str]]:
        return [{"id": "meera", "name": "Meera"}]

    async def health_check(self) -> bool:
        return bool(self.api_key)
