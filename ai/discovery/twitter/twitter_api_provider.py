import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from ai.discovery.twitter.models import TweetModel
from ai.discovery.twitter.twitter_client import TwitterClient

logger = logging.getLogger("Zem.TwitterAPIProvider")

class BaseTrendProvider(ABC):
    """Abstract base class for X/Twitter trend and hashtag ingestion."""
    
    @abstractmethod
    async def fetch_trends(self, limit: int = 15) -> List[TweetModel]:
        """Fetch popular/trending tweets."""
        pass
        
    @abstractmethod
    async def search_hashtags(self, hashtag: str, limit: int = 10) -> List[TweetModel]:
        """Fetch tweets matching a specific hashtag."""
        pass


class TwitterAPIProvider(BaseTrendProvider):
    """Ingestion provider using the official Twitter API v2."""

    def __init__(self, client: Optional[TwitterClient] = None):
        self.client = client or TwitterClient()

    async def fetch_trends(self, limit: int = 15) -> List[TweetModel]:
        logger.info(f"Fetching trends using Twitter API v2 (limit: {limit})")
        raw_tweets = await self.client.get_trending_tweets(max_results=limit)
        return self._to_tweet_models(raw_tweets)

    async def search_hashtags(self, hashtag: str, limit: int = 10) -> List[TweetModel]:
        logger.info(f"Searching hashtag #{hashtag} using Twitter API v2")
        query = f"#{hashtag} -is:retweet lang:en"
        raw_tweets = await self.client.search_tweets(query, max_results=limit)
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
                logger.error(f"Error converting tweet dictionary to Pydantic: {e}")
        return models
