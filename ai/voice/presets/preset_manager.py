import os
import yaml
import json
from shared.redis.client import redis_manager
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
from .models import VoicePreset, EmotionalTone, NarrationStyle
from .voice_registry import VoiceRegistry
from .emotion_mapper import EmotionMapper
from .tone_controller import ToneController
from .config_loader import ConfigLoader

logger = logging.getLogger(__name__)

class PresetManager:
    """
    Manages loading, validation, and caching of Voice Presets.
    """
    
    def __init__(self, config_dir: str = "voice_presets", use_redis: bool = True):
        self.config_dir = Path(config_dir)
        self.presets: Dict[str, VoicePreset] = {}
        self.use_redis = use_redis
        
        if not self.config_dir.exists():
            self.config_dir.mkdir(parents=True, exist_ok=True)

    async def load_all_presets(self):
        """Loads all YAML/JSON presets from the config directory."""
        if not self.config_dir.exists():
            logger.warning(f"Config directory {self.config_dir} does not exist.")
            return

        for file_path in self.config_dir.glob("*.*"):
            if file_path.suffix in [".yaml", ".yml", ".json"]:
                await self.load_preset_from_file(file_path)

    async def load_preset_from_file(self, file_path: Path):
        try:
            preset = ConfigLoader.load_preset(file_path)
            self.presets[preset.preset_name] = preset
            logger.info(f"Loaded preset: {preset.preset_name}")
        except Exception as e:
            logger.error(f"Failed to load preset from {file_path}: {e}")

    async def get_preset(self, preset_name: str) -> VoicePreset:
        """Retrieves a preset by name with fallback logic and caching."""
        # 1. Check in-memory cache
        if preset_name in self.presets:
            return self.presets[preset_name]
        
        # 2. Check Redis cache
        if self.use_redis:
            try:
                cached_data = await redis_manager.get_cache(f"voice_preset:{preset_name}")
                if cached_data:
                    preset = VoicePreset(**json.loads(cached_data))
                    self.presets[preset_name] = preset
                    return preset
            except Exception as e:
                logger.error(f"Redis cache lookup failed for {preset_name}: {e}")

        # 3. Load from file
        yaml_path = self.config_dir / f"{preset_name}.yaml"
        if yaml_path.exists():
            await self.load_preset_from_file(yaml_path)
            preset = self.presets.get(preset_name)
            
            # Update Redis cache
            if preset and self.use_redis:
                await redis_manager.set_cache(f"voice_preset:{preset_name}", preset.json())
            
            return preset
            
        raise ValueError(f"Preset '{preset_name}' not found.")

    def validate_preset(self, preset: VoicePreset) -> bool:
        """Validates if the preset's voice is supported by the provider."""
        return VoiceRegistry.is_voice_supported(preset.provider, preset.voice_name)

    async def save_preset(self, preset: VoicePreset):
        """Saves a preset to a YAML file."""
        self.presets[preset.preset_name] = preset
        file_path = self.config_dir / f"{preset.preset_name}.yaml"
        with open(file_path, "w") as f:
            yaml.dump(preset.dict(), f)
        logger.info(f"Saved preset {preset.preset_name} to {file_path}")

    async def get_final_config(self, preset_name: str, emotion: Optional[EmotionalTone] = None) -> Dict[str, Any]:
        """
        Gets the final configuration for a provider, merging preset, emotion, and tone settings.
        """
        preset = await self.get_preset(preset_name)
        config = preset.dict()
        
        if emotion:
            config = EmotionMapper.apply_emotion_to_preset(config, emotion)
            
        # Apply tone adjustments based on style
        config = ToneController.adjust_tone(config, preset.narration_style)
        
        return config
