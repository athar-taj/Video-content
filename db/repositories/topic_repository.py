from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from db.models.reddit_topic import RedditTopic
from typing import List, Optional, Dict, Any

class TopicRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_reddit_id(self, reddit_id: str) -> Optional[RedditTopic]:
        stmt = select(RedditTopic).where(RedditTopic.reddit_id == reddit_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, data: Dict[str, Any]) -> RedditTopic:
        topic = RedditTopic(**data)
        self.session.add(topic)
        await self.session.flush()
        return topic

    async def update_status(self, topic_id: int, status: str, stage: str = None):
        values = {"processing_status": status}
        if stage:
            values["processing_stage"] = stage
            
        stmt = update(RedditTopic).where(RedditTopic.id == topic_id).values(**values)
        await self.session.execute(stmt)

    async def list_topics(self, status: str = None, limit: int = 50) -> List[RedditTopic]:
        stmt = select(RedditTopic)
        if status:
            stmt = stmt.where(RedditTopic.processing_status == status)
        stmt = stmt.limit(limit).order_by(RedditTopic.inserted_at.desc())
        result = await self.session.execute(stmt)
        return result.scalars().all()
