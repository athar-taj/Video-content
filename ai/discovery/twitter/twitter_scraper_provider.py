import logging
from typing import List, Dict, Any, Optional
from ai.discovery.twitter.models import TweetModel
from ai.discovery.twitter.twitter_api_provider import BaseTrendProvider
from ai.discovery.twitter.twitter_client import TwitterClient

logger = logging.getLogger("Zem.TwitterScraperProvider")

class TwitterScraperProvider(BaseTrendProvider):
    """Scraper-based ingestion provider for X/Twitter."""

    def __init__(self, client: Optional[TwitterClient] = None):
        self.client = client or TwitterClient()

    async def fetch_trends(self, limit: int = 15) -> List[TweetModel]:
        logger.info(f"Fetching trends using X/Twitter Scraper (limit: {limit})")
        # Direct call to scraper fallback
        raw_tweets = await self.client._scrape_tweets_fallback("min_faves:500 (lang:en)", max_results=limit)
        return self._to_tweet_models(raw_tweets)

    async def search_hashtags(self, hashtag: str, limit: int = 10) -> List[TweetModel]:
        logger.info(f"Searching hashtag #{hashtag} using X/Twitter Scraper")
        raw_tweets = await self.client._scrape_tweets_fallback(f"#{hashtag}", max_results=limit)
        return self._to_tweet_models(raw_tweets)

    def _to_tweet_models(self, raw_tweets: List[Dict[str, Any]]) -> List[TweetModel]:
        models = []
        for t in raw_tweets:
            try:
                models.append(TweetModel(
                    tweet_id=t["tweet_id"],
                    author=t["author"],
                    content=t["content"],
                    created_at=t["created_at"],
                    likes=t["likes"],
                    retweets=t["retweets"],
                    replies=t["replies"],
                    quotes=t["quotes"],
                    hashtags=t["hashtags"]
                ))
            except Exception as e:
                logger.error(f"Error converting scraped tweet to model: {e}")
        return models
