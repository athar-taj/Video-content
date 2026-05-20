import asyncpraw
from typing import Optional
from shared.config.settings import settings
from shared.logging.logger import log

class RedditClient:
    """Async Reddit client manager using asyncpraw."""
    
    def __init__(self):
        self._reddit: Optional[asyncpraw.Reddit] = None

    async def get_instance(self) -> asyncpraw.Reddit:
        if not self._reddit:
            if not all([settings.REDDIT_CLIENT_ID, settings.REDDIT_CLIENT_SECRET]):
                log.error("Reddit credentials missing in configuration")
                raise ValueError("Reddit credentials missing")
                
            self._reddit = asyncpraw.Reddit(
                client_id=settings.REDDIT_CLIENT_ID,
                client_secret=settings.REDDIT_CLIENT_SECRET,
                user_agent=settings.REDDIT_USER_AGENT
            )
            log.info("Reddit client initialized")
        return self._reddit

    async def close(self):
        if self._reddit:
            await self._reddit.close()
            self._reddit = None
            log.info("Reddit client closed")

reddit_client = RedditClient()
