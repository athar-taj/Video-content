from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.models.database import RedditTopic, RedditComment
from datetime import datetime
from typing import List, Dict, Any, Optional

class DiscoveryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def topic_exists(self, reddit_id: str) -> bool:
        stmt = select(RedditTopic).where(RedditTopic.reddit_id == reddit_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def save_reddit_topic(self, data: Dict[str, Any]) -> RedditTopic:
        topic = RedditTopic(
            reddit_id=data["reddit_id"],
            subreddit=data["subreddit"],
            title=data["title"],
            body=data["body"],
            author=data["author"],
            score=data["score"],
            comments_count=data["comments_count"],
            viral_score=data.get("viral_score", 0.0),
            is_nsfw=data["is_nsfw"],
            permalink=data["permalink"],
            created_utc=datetime.fromtimestamp(data["created_utc"])
        )
        self.session.add(topic)
        await self.session.flush()
        return topic

    async def save_reddit_comments(self, topic_id: int, comments_data: List[Dict[str, Any]]):
        for c in comments_data:
            comment = RedditComment(
                topic_id=topic_id,
                comment_body=c["comment_body"],
                score=c["score"],
                author=c["author"],
                replies_count=c.get("replies_count", 0)
            )
            self.session.add(comment)
        await self.session.flush()
