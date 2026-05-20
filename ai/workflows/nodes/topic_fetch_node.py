import logging
from datetime import datetime
from typing import Dict, Any
from db.repositories.manager import db_manager
from sqlalchemy import select
from db.models.reddit_topic import RedditTopic
from db.models.database import Topic

logger = logging.getLogger(__name__)

async def topic_fetch_node(state: Dict[str, Any]) -> Dict[str, Any]:
    logger.info("Executing Fetch Topic Node...")
    
    topic_id = state.get("topic_id")
    
    async for session in db_manager.get_session():
        topic = None
        if topic_id:
            # Attempt to query RedditTopic by ID or reddit_id
            if str(topic_id).isdigit():
                stmt = select(RedditTopic).where(RedditTopic.id == int(topic_id))
            else:
                stmt = select(RedditTopic).where(RedditTopic.reddit_id == topic_id)
            res = await session.execute(stmt)
            topic = res.scalar_one_or_none()
            
            if not topic:
                # Attempt to query user Topic
                if str(topic_id).isdigit():
                    stmt = select(Topic).where(Topic.id == int(topic_id))
                    res = await session.execute(stmt)
                    user_topic = res.scalar_one_or_none()
                    if user_topic:
                        logger.info(f"Fetched user topic: {user_topic.title}")
                        return {
                            "topic_id": str(user_topic.id),
                            "execution_metadata": {
                                "title": user_topic.title,
                                "body": user_topic.content or "",
                                "subreddit": "user"
                            }
                        }
        else:
            # Fetch top ranked topic
            stmt = select(RedditTopic).order_by(RedditTopic.viral_score.desc()).limit(1)
            res = await session.execute(stmt)
            topic = res.scalar_one_or_none()
            
        if not topic:
            logger.warning("No topics found in the database. Checking for existing fallback mock topic.")
            stmt = select(RedditTopic).where(RedditTopic.reddit_id == "mock_topic_id")
            res = await session.execute(stmt)
            existing_mock = res.scalar_one_or_none()
            if existing_mock:
                logger.info(f"Found existing fallback mock topic in database with ID: {existing_mock.id}")
                return {
                    "topic_id": str(existing_mock.id),
                    "execution_metadata": {
                        "title": existing_mock.title,
                        "body": existing_mock.body or "",
                        "subreddit": existing_mock.subreddit
                    }
                }

            logger.warning("Mock topic not found in database. Creating default mock topic in database.")
            mock_topic = RedditTopic(
                reddit_id="mock_topic_id",
                subreddit="gaming",
                title="Why Minecraft is still the best game",
                body="It allows for absolute creative freedom and endless updates.",
                author="mock_author",
                score=100,
                comments_count=10,
                viral_score=95.0,
                is_nsfw=False,
                permalink="/r/gaming/comments/mock",
                created_utc=datetime.utcnow()
            )
            session.add(mock_topic)
            await session.commit()
            logger.info(f"Created default mock topic in database with ID: {mock_topic.id}")
            return {
                "topic_id": str(mock_topic.id),
                "execution_metadata": {
                    "title": mock_topic.title,
                    "body": mock_topic.body or "",
                    "subreddit": mock_topic.subreddit
                }
            }
            
        logger.info(f"Fetched Reddit topic: {topic.title} (ID: {topic.id})")
        return {
            "topic_id": str(topic.id),
            "execution_metadata": {
                "title": topic.title,
                "body": topic.body or "",
                "subreddit": topic.subreddit
            }
        }
