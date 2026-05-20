from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class TTSResponse(BaseModel):
    audio_path: str
    provider: str
    voice: str
    duration_sec: float
    file_size_bytes: int
    metadata: Dict[str, Any] = {}

class BaseTTSProvider(ABC):
    """Abstract base class for all Text-to-Speech providers."""
    
    @abstractmethod
    async def generate_audio(self, text: str, voice_id: str, output_path: str, **kwargs) -> TTSResponse:
        """Converts text to audio and saves it to output_path."""
        pass

    @abstractmethod
    async def get_available_voices(self) -> List[Dict[str, str]]:
        """Returns a list of available voice profiles."""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Checks if the provider API/Service is reachable."""
        pass
