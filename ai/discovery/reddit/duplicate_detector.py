from rapidfuzz import fuzz
from typing import List, Optional
from shared.config.settings import settings
from shared.redis.client import redis_manager
from shared.logging.logger import log

class DuplicateDetector:
    """Detects duplicate or highly similar content using fuzzy matching and Redis caching."""
    
    @staticmethod
    def calculate_similarity(text1: str, text2: str) -> float:
        """Returns similarity score between 0 and 100."""
        return fuzz.token_set_ratio(text1, text2)

    @classmethod
    async def is_duplicate_in_cache(cls, content_hash: str) -> bool:
        """Checks Redis if a content hash already exists."""
        if not redis_manager.client:
            return False
            
        exists = await redis_manager.get_cache(f"dup:{content_hash}")
        return exists is not None

    @classmethod
    async def mark_as_seen(cls, content_hash: str, ttl: int = 86400):
        """Marks a hash as seen in Redis for 24 hours."""
        if redis_manager.client:
            await redis_manager.set_cache(f"dup:{content_hash}", "1", expire=ttl)

    @staticmethod
    def check_title_similarity(new_title: str, existing_titles: List[str]) -> bool:
        """Checks if a new title is too similar to any in a list of existing titles."""
        for existing in existing_titles:
            score = fuzz.token_set_ratio(new_title, existing)
            if score >= settings.SIMILARITY_THRESHOLD:
                log.debug(f"Similarity too high: {score}% between '{new_title[:30]}' and '{existing[:30]}'")
                return True
        return False
