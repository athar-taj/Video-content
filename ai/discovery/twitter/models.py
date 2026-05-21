from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class TweetModel(BaseModel):
    tweet_id: str = Field(..., description="Unique Tweet ID string")
    author: str = Field(..., description="Username of tweet creator")
    content: str = Field(..., description="Raw text content of the tweet")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Engagement metrics
    likes: int = Field(default=0)
    retweets: int = Field(default=0)
    replies: int = Field(default=0)
    quotes: int = Field(default=0)
    views: Optional[int] = Field(default=None)
    
    # Metadata
    hashtags: List[str] = Field(default_factory=list)
    mentions: List[str] = Field(default_factory=list)
    urls: List[str] = Field(default_factory=list)
    
    # Virality analysis
    engagement_score: float = Field(default=0.0)
    viral_score: float = Field(default=0.0)
    emotional_score: float = Field(default=0.0)
    retention_score: float = Field(default=0.0)
    sentiment: str = Field(default="neutral")
    hook: Optional[str] = Field(default=None)


class TrendClusterModel(BaseModel):
    cluster_name: str = Field(..., description="Semantic cluster topic name")
    cluster_score: float = Field(default=0.0, description="Aggregate virality score of the cluster")
    tweets: List[TweetModel] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class InfluencerModel(BaseModel):
    username: str = Field(..., description="Username identifier")
    followers: int = Field(default=0)
    following: int = Field(default=0)
    influence_score: float = Field(default=0.0)
    engagement_rate: float = Field(default=0.0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
