import logging
from typing import Dict, Any, Optional
from ai.discovery.twitter.models import InfluencerModel

logger = logging.getLogger("Zem.InfluencerDetector")

class InfluencerDetector:
    """
    Identifies high-impact creators/accounts and calculates an influence/authority score.
    Helps prioritize trends originating from authoritative voices.
    """
    @staticmethod
    def calculate_influence(followers: int, following: int, average_likes: float, average_retweets: float) -> InfluencerModel:
        """
        Calculates and returns an InfluencerModel with calculated influence_score and engagement_rate.
        """
        # Engagement rate: (average engagement / followers) * 100
        # If followers is 0, default to low baseline
        engagement_rate = 0.0
        if followers > 0:
            total_eng = average_likes + (average_retweets * 2.0)
            engagement_rate = min(100.0, (total_eng / followers) * 100.0)
            
        # Influence score: logarithmic scale of followers + engagement multiplier
        import math
        follower_log = math.log10(max(1.0, followers)) # e.g. 100k followers -> log10(100,000) = 5
        
        # Base score on followers (scaled 0-50)
        base_score = min(50.0, follower_log * 7.5)
        
        # Engagement bonus (scaled 0-50)
        eng_bonus = min(50.0, engagement_rate * 5.0)
        
        influence_score = base_score + eng_bonus
        
        # Normalize to 0-100
        influence_score = max(0.0, min(100.0, influence_score))
        
        return InfluencerModel(
            username="",  # Set by caller
            followers=followers,
            following=following,
            influence_score=round(influence_score, 2),
            engagement_rate=round(engagement_rate, 4)
        )

    @classmethod
    def analyze_author_tweet(cls, author_name: str, tweet_likes: int, tweet_retweets: int) -> InfluencerModel:
        """
        Analyzes a single tweet from an author to estimate/calculate their influencer profile.
        Used as a quick heuristic when full profile details are not fetched.
        """
        # If we only have tweet engagement, estimate followers heuristically
        # e.g., standard engagement is ~1-3% of followers. Assume 2% engagement rate.
        estimated_followers = int((tweet_likes + tweet_retweets * 2) * 50)
        estimated_followers = max(500, estimated_followers) # Minimum baseline
        
        model = cls.calculate_influence(
            followers=estimated_followers,
            following=int(estimated_followers * 0.4),
            average_likes=tweet_likes,
            average_retweets=tweet_retweets
        )
        model.username = author_name
        return model
