import asyncio
import sys
import os
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).parent.parent))

from ai.voice.presets.preset_manager import PresetManager
from ai.voice.presets.voice_router import VoiceRouter
from ai.voice.presets.models import EmotionalTone
from shared.logging.logger import log

async def main():
    log.info("Starting Voice Preset System Test...")
    
    # 1. Initialize Manager and Router
    preset_manager = PresetManager(config_dir="voice_presets", use_redis=False) # Disable redis for local test if not running
    voice_router = VoiceRouter(preset_manager)
    
    # 2. Load presets
    await preset_manager.load_all_presets()
    
    test_cases = [
        {"niche": "horror", "emotion": EmotionalTone.SUSPENSE},
        {"niche": "motivation", "emotion": EmotionalTone.ENERGETIC},
        {"niche": "breakup", "emotion": EmotionalTone.EMOTIONAL},
        {"niche": "documentary", "emotion": EmotionalTone.CALM},
    ]
    
    for case in test_cases:
        log.info(f"--- Testing Niche: {case['niche']} ---")
        
        # Select preset via router
        preset_data = await voice_router.get_preset_for_script(niche=case['niche'])
        preset_name = preset_data['preset_name']
        log.info(f"Selected Preset: {preset_name}")
        
        # Generate final configuration with emotional mapping and tone control
        final_config = await preset_manager.get_final_config(
            preset_name=preset_name, 
            emotion=case['emotion']
        )
        
        log.info(f"Final Voice Config for {case['niche']}:")
        for key, value in final_config.items():
            if key in ['provider', 'voice_name', 'speech_speed', 'pitch', 'energy', 'emotional_tone']:
                log.info(f"  {key}: {value}")

    log.info("Voice Preset System Test Completed Successfully.")

if __name__ == "__main__":
    asyncio.run(main())
