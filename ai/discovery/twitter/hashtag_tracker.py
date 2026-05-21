import logging
from typing import List, Dict
from ai.discovery.twitter.models import TweetModel

logger = logging.getLogger("Zem.HashtagTracker")

class HashtagTracker:
    """Tracks and forecasts momentum for trending hashtags on X."""
    
    def __init__(self):
        self.hashtag_history: Dict[str, List[int]] = {}

    def track_hashtag_growth(self, hashtag: str, current_volume: int) -> float:
        """Calculate momentum based on volume growth."""
        hashtag_lower = hashtag.lower().strip("#")
        history = self.hashtag_history.setdefault(hashtag_lower, [])
        history.append(current_volume)
        
        # Keep only last 5 entries
        if len(history) > 5:
            history.pop(0)
            
        if len(history) < 2:
            return 0.0 # No trend data yet
            
        # calculate percentage growth from previous
        prev = history[-2]
        if prev == 0:
            return 100.0
        growth = ((history[-1] - prev) / prev) * 100.0
        return round(growth, 2)
