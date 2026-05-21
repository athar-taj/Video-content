import logging
import asyncio
import time
from typing import Dict

logger = logging.getLogger("Zem.RateLimitManager")

class RateLimitManager:
    """
    Manages request scheduling and cooldown windows for Twitter API v2 and Scraping.
    Prevents account blocks and endpoint rate limit errors by spacing requests.
    """
    def __init__(self):
        # Maps endpoint/provider to last request timestamp
        self._last_request_time: Dict[str, float] = {}
        
        # Default cooldowns (in seconds) between requests for various providers
        self.cooldowns = {
            "api_search": 5.0,     # API limits are generally more forgiving but let's be safe
            "api_trends": 10.0,
            "scraper_search": 15.0, # Scraper needs longer gaps to avoid bot detection
            "scraper_trends": 20.0
        }

    async def wait_if_needed(self, endpoint: str):
        """
        Calculates elapsed time since the last request to the given endpoint,
        and sleeps for the remaining cooldown duration if necessary.
        """
        now = time.time()
        last_time = self._last_request_time.get(endpoint, 0.0)
        cooldown = self.cooldowns.get(endpoint, 5.0)
        
        elapsed = now - last_time
        if elapsed < cooldown:
            sleep_time = cooldown - elapsed
            logger.info(f"RateLimitManager: Sleeping for {sleep_time:.2f}s before accessing '{endpoint}'...")
            await asyncio.sleep(sleep_time)
            
        # Update last request time to current time (after sleep finishes)
        self._last_request_time[endpoint] = time.time()

# Global singleton instance
rate_limit_manager = RateLimitManager()
