from typing import Optional, Dict, Any
from .models import NarrationStyle, EmotionalTone
from .preset_manager import PresetManager

class VoiceRouter:
    """
    Routes script content to the appropriate voice preset based on niche and emotional context.
    """
    
    NICHE_MAPPING = {
        "horror": "horror_narrator",
        "mystery": "suspense_male",
        "romance": "emotional_female",
        "breakup": "emotional_female",
        "motivation": "motivational_fast",
        "documentary": "storytelling_calm",
        "news": "steady_reporter"
    }

    def __init__(self, preset_manager: PresetManager):
        self.preset_manager = preset_manager

    async def get_preset_for_script(
        self, 
        niche: str, 
        script_type: Optional[str] = None,
        overrides: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Selects and configures a voice preset based on the script's niche and type.
        """
        # 1. Determine preset name from mapping
        preset_name = self.NICHE_MAPPING.get(niche.lower())
        if not preset_name and script_type:
             preset_name = self.NICHE_MAPPING.get(script_type.lower())
        
        # Fallback
        if not preset_name:
            preset_name = "storytelling_calm"

        # 2. Load the preset
        preset = await self.preset_manager.get_preset(preset_name)
        
        # 3. Apply overrides if provided
        if overrides:
            preset_data = preset.dict()
            preset_data.update(overrides)
            # Re-validate or just use the dict
            return preset_data
            
        return preset.dict()

    async def route_by_emotion(self, content_emotion: str) -> str:
        """Helper to find the best preset for a detected emotion."""
        emotion_to_preset = {
            "sad": "emotional_female",
            "scary": "horror_narrator",
            "angry": "dramatic_male",
            "happy": "energetic_female"
        }
        return emotion_to_preset.get(content_emotion.lower(), "storytelling_calm")
