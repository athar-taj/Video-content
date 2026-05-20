import random
import logging
from typing import List, Optional
from ai.video_assets.backgrounds.models import VideoAsset
from shared.redis.client import redis_manager

logger = logging.getLogger(__name__)

class VideoSelector:
    """
    Selects background videos based on niche, duration, and repetition history.
    """
    
    def __init__(self, assets: List[VideoAsset]):
        self.assets = assets

    async def select_video(self, category: str, required_duration: float, tags: List[str] = []) -> Optional[VideoAsset]:
        """
        Filters assets by category and tags, then selects one randomly while avoiding duplicates.
        """
        # Filter by category
        eligible = [a for a in self.assets if a.category == category]
        
        # Filter by duration (prefer assets longer than required, but we can loop if needed)
        # For now, just prefer longer assets
        long_enough = [a for a in eligible if a.duration_seconds >= required_duration]
        candidates = long_enough if long_enough else eligible
        
        # Filter by tags if provided
        if tags:
            with_tags = [a for a in candidates if any(t in a.tags for t in tags)]
            if with_tags:
                candidates = with_tags
        
        if not candidates:
            logger.warning(f"No candidates found for category {category} and tags {tags}")
            return None

        # Repetition avoidance using Redis
        # Sort candidates by "recency" or just shuffle and try
        random.shuffle(candidates)
        
        for asset in candidates:
            cache_key = f"asset_usage:{asset.id}"
            usage_count = await redis_manager.get_cache(cache_key)
            if not usage_count or int(usage_count) < 3: # Allow 3 uses before "cooling down"
                # Record usage (increment in actual pipeline)
                return asset
                
        # If all were used recently, just pick the first one
        return candidates[0]
