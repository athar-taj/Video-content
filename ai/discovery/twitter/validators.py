import logging
from ai.discovery.twitter.models import TweetModel

logger = logging.getLogger("Zem.TwitterValidators")

class TweetValidator:
    """
    Validates ingested tweets to ensure they meet basic structure and quality standards.
    Prevents corrupt or trash tweets from entering the DB/LangGraph pipelines.
    """
    @staticmethod
    def validate_tweet(tweet: TweetModel) -> bool:
        """
        Validates a single TweetModel instance.
        Returns True if valid, False if it should be discarded.
        """
        # 1. Validate basic ID and content presence
        if not tweet.tweet_id or not tweet.tweet_id.isdigit():
            logger.warning(f"Discarding tweet: Invalid tweet_id '{tweet.tweet_id}'")
            return False
            
        if not tweet.author or len(tweet.author.strip()) == 0:
            logger.warning(f"Discarding tweet {tweet.tweet_id}: Author name is empty")
            return False
            
        if not tweet.content or len(tweet.content.strip()) < 10:
            logger.warning(f"Discarding tweet {tweet.tweet_id}: Content is too short (< 10 chars)")
            return False
            
        # 2. Check for suspicious/spam patterns (e.g., too many links or hashtags)
        if len(tweet.urls) > 4:
            logger.warning(f"Discarding tweet {tweet.tweet_id}: Too many URLs ({len(tweet.urls)}) - likely spam")
            return False
            
        if len(tweet.hashtags) > 6:
            logger.warning(f"Discarding tweet {tweet.tweet_id}: Hashtag stuffing ({len(tweet.hashtags)}) - likely low-quality")
            return False
            
        # 3. Validate engagement metrics
        if tweet.likes < 0 or tweet.retweets < 0 or tweet.replies < 0 or tweet.quotes < 0:
            logger.warning(f"Discarding tweet {tweet.tweet_id}: Negative engagement metrics detected")
            return False
            
        return True

    @classmethod
    def filter_valid_tweets(cls, tweets: list[TweetModel]) -> list[TweetModel]:
        """Filters a list of TweetModels, keeping only valid ones."""
        valid_tweets = []
        for t in tweets:
            if cls.validate_tweet(t):
                valid_tweets.append(t)
        logger.info(f"Validator: Approved {len(valid_tweets)} out of {len(tweets)} parsed tweets.")
        return valid_tweets
