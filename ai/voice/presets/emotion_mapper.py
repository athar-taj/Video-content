from typing import Dict, Any
from .models import EmotionalTone

class EmotionMapper:
    """
    Maps high-level emotional tones to provider-specific parameters.
    """
    
    EMOTION_CONFIGS = {
        EmotionalTone.SUSPENSE: {
            "speech_speed": 0.9,
            "stability": 0.8,
            "energy": 0.4,
            "pitch": -2.0,
            "murf_style": "whisper",
            "kokoro_pacing": "slow"
        },
        EmotionalTone.ENERGETIC: {
            "speech_speed": 1.15,
            "stability": 0.5,
            "energy": 0.9,
            "pitch": 1.5,
            "murf_style": "cheerful",
            "kokoro_pacing": "fast"
        },
        EmotionalTone.DRAMATIC: {
            "speech_speed": 0.95,
            "stability": 0.7,
            "energy": 0.6,
            "pitch": -1.0,
            "pause_style": "dramatic"
        },
        EmotionalTone.CALM: {
            "speech_speed": 0.9,
            "stability": 0.9,
            "energy": 0.3,
            "pitch": 0.0,
            "pause_style": "natural"
        },
        EmotionalTone.MOTIVATIONAL: {
            "speech_speed": 1.05,
            "stability": 0.6,
            "energy": 0.8,
            "pitch": 1.0,
            "pacing_style": "dynamic"
        }
    }

    @classmethod
    def get_emotion_settings(cls, tone: EmotionalTone) -> Dict[str, Any]:
        """Returns normalized settings for a given emotion."""
        return cls.EMOTION_CONFIGS.get(tone, cls.EMOTION_CONFIGS[EmotionalTone.CALM])

    @classmethod
    def apply_emotion_to_preset(cls, preset_data: Dict[str, Any], tone: EmotionalTone) -> Dict[str, Any]:
        """Merges emotion settings into preset data."""
        emotion_settings = cls.get_emotion_settings(tone)
        updated_data = preset_data.copy()
        updated_data.update(emotion_settings)
        return updated_data
