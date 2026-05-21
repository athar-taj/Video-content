import logging
from datetime import datetime, timezone
from typing import List
from ai.discovery.twitter.models import TweetModel

logger = logging.getLogger("Zem.TrendDetector")

class TrendDetector:
    """
    Detects trending signals, engagement spikes, and topic momentum.
    Calculates engagement velocity over time.
    """

    def calculate_velocity(self, tweet: TweetModel) -> float:
        """
        Calculate engagement velocity per hour.
        Formula: (likes + retweets * 2.5 + replies * 3.0 + quotes * 4.0) / age_in_hours
        """
        now = datetime.utcnow()
        # Ensure UTC comparison
        created_time = tweet.created_at.replace(tzinfo=None)
        age_delta = now - created_time
        age_hours = age_delta.total_seconds() / 3600.0
        
        # Guard against zero division, min age of 30 minutes
        adjusted_hours = max(0.5, age_hours)
        
        total_interactions = (
            tweet.likes * 1.0 +
            tweet.retweets * 2.5 +
            tweet.replies * 3.0 +
            tweet.quotes * 4.0
        )
        
        velocity = total_interactions / adjusted_hours
        return round(velocity, 2)

    def detect_spikes(self, tweets: List[TweetModel]) -> List[TweetModel]:
        """Filter and return tweets that exhibit a high engagement spike."""
        spiked_tweets = []
        for tweet in tweets:
            velocity = self.calculate_velocity(tweet)
            tweet.engagement_score = velocity
            
            # Simple threshold check for a spiked tweet: velocity > 100/hr
            if velocity > 100.0 or (tweet.likes + tweet.retweets) > 500:
                logger.info(f"Emerging spike detected for tweet {tweet.tweet_id} by @{tweet.author} (Vel: {velocity}/hr)")
                spiked_tweets.append(tweet)
                
        return spiked_tweets

    def detect_trending_hashtags(self, tweets: List[TweetModel]) -> List[str]:
        """Aggregate and rank popular hashtags."""
        tags_map = {}
        for t in tweets:
            for tag in t.hashtags:
                normalized = tag.lower()
                # Weight by tweet engagement
                tags_map[normalized] = tags_map.get(normalized, 0) + (t.likes + t.retweets * 3)

        sorted_tags = sorted(tags_map.items(), key=lambda x: x[1], reverse=True)
        return [tag for tag, score in sorted_tags if score > 50]
