import logging
from datetime import datetime
from typing import Dict, Any
from db.repositories.manager import db_manager
from sqlalchemy import select
from db.models.reddit_topic import RedditTopic
from db.models.twitter_discovery import TwitterTrend
from db.models.database import Topic

logger = logging.getLogger(__name__)

async def topic_fetch_node(state: Dict[str, Any]) -> Dict[str, Any]:
    logger.info("Executing Fetch Topic Node...")
    
    topic_id = state.get("topic_id")
    
    async with db_manager.get_session() as session:
        topic = None
        source_type = "twitter"
        
        if topic_id:
            # 1. Query TwitterTrend by ID or tweet_id
            if str(topic_id).isdigit():
                stmt = select(TwitterTrend).where(TwitterTrend.id == int(topic_id))
            else:
                stmt = select(TwitterTrend).where(TwitterTrend.tweet_id == topic_id)
            res = await session.execute(stmt)
            topic = res.scalar_one_or_none()
            
            if topic:
                source_type = "twitter"
            else:
                # 2. Query RedditTopic by ID or reddit_id
                if str(topic_id).isdigit():
                    stmt = select(RedditTopic).where(RedditTopic.id == int(topic_id))
                else:
                    stmt = select(RedditTopic).where(RedditTopic.reddit_id == topic_id)
                res = await session.execute(stmt)
                topic = res.scalar_one_or_none()
                
                if topic:
                    source_type = "reddit"
                else:
                    # 3. Query user Topic
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
                                    "subreddit": "user",
                                    "source": "user",
                                    "forced_score": state.get("execution_metadata", {}).get("forced_score")
                                }
                            }
        else:
            # Fetch top ranked topic: try Twitter first, then Reddit
            stmt = select(TwitterTrend).order_by(TwitterTrend.viral_score.desc()).limit(1)
            res = await session.execute(stmt)
            topic = res.scalar_one_or_none()
            
            if topic:
                source_type = "twitter"
            else:
                stmt = select(RedditTopic).order_by(RedditTopic.viral_score.desc()).limit(1)
                res = await session.execute(stmt)
                topic = res.scalar_one_or_none()
                if topic:
                    source_type = "reddit"
            
        if not topic:
            logger.warning("No topics/trends found in the database. Checking for existing fallback mock Twitter trend.")
            stmt = select(TwitterTrend).where(TwitterTrend.tweet_id == "mock_tweet_id")
            res = await session.execute(stmt)
            existing_mock = res.scalar_one_or_none()
            if existing_mock:
                logger.info(f"Found existing fallback mock Twitter trend in database with ID: {existing_mock.id}")
                first_words = " ".join(existing_mock.content.split()[:5]) + "..."
                return {
                    "topic_id": str(existing_mock.id),
                    "execution_metadata": {
                        "title": f"Twitter Trend: {first_words}",
                        "body": existing_mock.content,
                        "subreddit": f"@{existing_mock.author}",
                        "source": "twitter",
                        "forced_score": 90.0 # Force a high score for mock test runs
                    }
                }

            logger.warning("Mock trend not found in database. Creating default mock Twitter trend in database.")
            mock_topic = TwitterTrend(
                tweet_id="mock_tweet_id",
                author="TechCrunch",
                content="AI startups are raising record capital despite market tightening. OpenAI's latest model updates have changed the unit economics of token generation entirely. Nobody saw this coming...",
                hashtags={"tags": ["AI", "Tech", "VentureCapital"]},
                engagement_score=482.0,
                viral_score=90.0,
                emotional_score=85.0,
                retention_score=85.0,
                processing_status="fetched",
                processing_stage="discovery",
                source_type="twitter"
            )
            session.add(mock_topic)
            await session.commit()
            logger.info(f"Created default mock Twitter trend in database with ID: {mock_topic.id}")
            first_words = " ".join(mock_topic.content.split()[:5]) + "..."
            return {
                "topic_id": str(mock_topic.id),
                "execution_metadata": {
                    "title": f"Twitter Trend: {first_words}",
                    "body": mock_topic.content,
                    "subreddit": f"@{mock_topic.author}",
                    "source": "twitter",
                    "forced_score": 90.0
                }
            }
            
        if source_type == "twitter":
            first_words = " ".join(topic.content.split()[:5]) + "..."
            logger.info(f"Fetched Twitter trend: {first_words} (ID: {topic.id})")
            return {
                "topic_id": str(topic.id),
                "execution_metadata": {
                    "title": f"Twitter Trend: {first_words}",
                    "body": topic.content,
                    "subreddit": f"@{topic.author}",
                    "source": "twitter",
                    "forced_score": topic.viral_score
                }
            }
        else:
            logger.info(f"Fetched Reddit topic: {topic.title} (ID: {topic.id})")
            return {
                "topic_id": str(topic.id),
                "execution_metadata": {
                    "title": topic.title,
                    "body": topic.body or "",
                    "subreddit": topic.subreddit,
                    "source": "reddit",
                    "forced_score": topic.viral_score
                }
            }

