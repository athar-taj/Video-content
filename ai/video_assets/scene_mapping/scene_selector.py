import logging
import random
from typing import List
from .models import Scene

logger = logging.getLogger(__name__)

class SceneSelector:
    """Selects visual assets based on emotion and niche."""
    
    # Dummy asset database for selection
    ASSET_DB = {
        "suspense": ["dark_gameplay_1.mp4", "creepy_hallway.mp4"],
        "emotional": ["cinematic_sunset.mp4", "slow_rain.mp4"],
        "motivation": ["fast_parkour.mp4", "gym_workout.mp4", "running_fast.mp4"],
        "horror": ["spooky_forest.mp4", "scary_basement.mp4"],
        "storytelling": ["subway_surfers_bg.mp4", "minecraft_parkour.mp4", "gta_car.mp4"]
    }

    def select_assets(self, scenes: List[Scene]) -> List[Scene]:
        """Assign assets to scenes based on their emotion/visual style."""
        logger.info("Selecting visual assets for scenes.")
        
        for scene in scenes:
            emotion = scene.emotion.lower()
            available_assets = self.ASSET_DB.get(emotion, self.ASSET_DB["storytelling"])
            
            # Select random asset to avoid repetition
            scene.asset_id = random.choice(available_assets)
            logger.debug(f"Assigned asset {scene.asset_id} to scene {scene.scene_id} (Emotion: {emotion})")
            
        return scenes
