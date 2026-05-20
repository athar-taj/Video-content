from typing import List, Dict, Any, Optional
from .models import VoicePreset, Gender, NarrationStyle, EmotionalTone

class VoiceRegistry:
    """
    Central registry for all supported AI voices across different providers.
    """
    
    # Predefined voices for initial setup
    DEFAULT_VOICES = {
        "sarvam": [
            {"name": "v1_male_1", "gender": Gender.MALE, "language": "hi-IN"},
            {"name": "v1_female_1", "gender": Gender.FEMALE, "language": "hi-IN"},
        ],
        "murf": [
            {"name": "marcus_deep", "gender": Gender.MALE, "language": "en-US"},
            {"name": "samantha_warm", "gender": Gender.FEMALE, "language": "en-US"},
        ],
        "kokoro": [
            {"name": "af_bella", "gender": Gender.FEMALE, "language": "en-US"},
            {"name": "am_adam", "gender": Gender.MALE, "language": "en-US"},
        ]
    }

    @classmethod
    def get_provider_voices(cls, provider: str) -> List[Dict[str, Any]]:
        return cls.DEFAULT_VOICES.get(provider.lower(), [])

    @classmethod
    def is_voice_supported(cls, provider: str, voice_name: str) -> bool:
        voices = cls.get_provider_voices(provider)
        return any(v["name"] == voice_name for v in voices)
