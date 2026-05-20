from typing import Dict, Any
from .models import NarrationStyle

class ToneController:
    """
    Controls narration rhythm, pacing, and energy levels based on niche and style.
    """
    
    STYLE_OVERRIDES = {
        NarrationStyle.DEEP: {
            "pitch": -3.0,
            "speech_speed": 0.85,
            "energy": 0.4
        },
        NarrationStyle.STORYTELLING: {
            "pacing_style": "dynamic",
            "pause_style": "natural",
            "stability": 0.7
        },
        NarrationStyle.SUSPENSE: {
            "pause_style": "dramatic",
            "speech_speed": 0.9,
            "energy": 0.3
        },
        NarrationStyle.MOTIVATIONAL: {
            "speech_speed": 1.1,
            "energy": 0.8,
            "pacing_style": "fast"
        }
    }

    @classmethod
    def adjust_tone(cls, base_config: Dict[str, Any], style: NarrationStyle) -> Dict[str, Any]:
        """
        Applies style-specific overrides to a base voice configuration.
        """
        overrides = cls.STYLE_OVERRIDES.get(style, {})
        final_config = base_config.copy()
        final_config.update(overrides)
        return final_config

    @classmethod
    def get_pacing_parameters(cls, pacing_style: str) -> Dict[str, Any]:
        """Returns specific timing parameters based on pacing style."""
        pacing_map = {
            "slow": {"speed": 0.8, "pause_multiplier": 1.5},
            "steady": {"speed": 1.0, "pause_multiplier": 1.0},
            "fast": {"speed": 1.2, "pause_multiplier": 0.8},
            "dynamic": {"speed": 1.0, "variable_pacing": True}
        }
        return pacing_map.get(pacing_style, pacing_map["steady"])
