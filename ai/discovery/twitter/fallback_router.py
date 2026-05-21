import logging
from typing import List, Optional
from ai.discovery.twitter.models import TweetModel
from ai.discovery.twitter.twitter_api_provider import TwitterAPIProvider
from ai.discovery.twitter.twitter_scraper_provider import TwitterScraperProvider
from ai.discovery.twitter.rate_limit_manager import rate_limit_manager
from ai.discovery.twitter.validators import TweetValidator

logger = logging.getLogger("Zem.TwitterFallbackRouter")

class TwitterFallbackRouter:
    """
    Orchestrates the discovery providers:
    TwitterAPIProvider (official v2) -> TwitterScraperProvider (Twikit/Scraper) -> Local Mock fallback.
    Maintains rate limiting controls and filters out invalid outputs.
    """
    def __init__(
        self,
        api_provider: Optional[TwitterAPIProvider] = None,
        scraper_provider: Optional[TwitterScraperProvider] = None
    ):
        self.api_provider = api_provider or TwitterAPIProvider()
        self.scraper_provider = scraper_provider or TwitterScraperProvider()

    async def fetch_trends(self, limit: int = 15) -> List[TweetModel]:
        """
        Fetches trends from the best available provider with fallback logic.
        """
        # Try API v2 first if enabled
        if self.api_provider.client.api_enabled:
            try:
                await rate_limit_manager.wait_if_needed("api_trends")
                tweets = await self.api_provider.fetch_trends(limit=limit)
                valid_tweets = TweetValidator.filter_valid_tweets(tweets)
                if valid_tweets:
                    logger.info(f"Successfully retrieved {len(valid_tweets)} trends from API v2.")
                    return valid_tweets
            except Exception as e:
                logger.error(f"API v2 failed to fetch trends: {e}. Falling back to Scraper.")

        # Fallback to Scraper (which includes deterministic mock fallback)
        try:
            await rate_limit_manager.wait_if_needed("scraper_trends")
            tweets = await self.scraper_provider.fetch_trends(limit=limit)
            valid_tweets = TweetValidator.filter_valid_tweets(tweets)
            logger.info(f"Successfully retrieved {len(valid_tweets)} trends from Scraper/Mock.")
            return valid_tweets
        except Exception as e:
            logger.critical(f"All trend ingestion providers failed, including mock fallbacks: {e}")
            return []

    async def search_hashtags(self, hashtag: str, limit: int = 10) -> List[TweetModel]:
        """
        Searches hashtag from the best available provider with fallback logic.
        """
        # Try API v2 first if enabled
        if self.api_provider.client.api_enabled:
            try:
                await rate_limit_manager.wait_if_needed("api_search")
                tweets = await self.api_provider.search_hashtags(hashtag, limit=limit)
                valid_tweets = TweetValidator.filter_valid_tweets(tweets)
                if valid_tweets:
                    logger.info(f"Successfully retrieved {len(valid_tweets)} search results for #{hashtag} from API v2.")
                    return valid_tweets
            except Exception as e:
                logger.error(f"API v2 failed for #{hashtag} search: {e}. Falling back to Scraper.")

        # Fallback to Scraper
        try:
            await rate_limit_manager.wait_if_needed("scraper_search")
            tweets = await self.scraper_provider.search_hashtags(hashtag, limit=limit)
            valid_tweets = TweetValidator.filter_valid_tweets(tweets)
            logger.info(f"Successfully retrieved {len(valid_tweets)} search results for #{hashtag} from Scraper/Mock.")
            return valid_tweets
        except Exception as e:
            logger.critical(f"All hashtag search providers failed: {e}")
            return []
