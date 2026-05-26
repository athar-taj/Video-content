from typing import List
from datetime import datetime
from sqlalchemy import select, update
from db.models.database import RedditTopic
from db.repositories.manager import db_manager
from ai.discovery.reddit.ranking import ViralScoreCalculator, TrendMetrics
from ai.discovery.reddit.duplicate_detector import DuplicateDetector
from shared.logging.logger import log

class TrendAnalyzer:
    """Orchestrates the ranking and trend analysis of discovered topics."""
    
    def __init__(self):
        self.calculator = ViralScoreCalculator()

    async def analyze_and_rank(self):
        """Load recent topics, calculate scores, and update rankings in DB."""
        log.info("📊 Starting trend analysis and ranking...")
        
        async with db_manager.get_session() as session:
            # 1. Fetch topics from the last 48 hours that haven't been processed recently
            stmt = select(RedditTopic).where(
                RedditTopic.inserted_at >= datetime.utcnow().replace(hour=0) # Simple filter for today
            )
            result = await session.execute(stmt)
            topics = result.scalars().all()
            
            log.info(f"Found {len(topics)} topics to analyze")
            
            for topic in topics:
                # 2. Calculate new scores
                metrics = TrendMetrics(
                    upvotes=int(topic.score),
                    comments_count=int(topic.comments_count),
                    created_utc=topic.created_utc.timestamp(),
                    title=topic.title,
                    body_length=len(topic.body) if topic.body else 0
                )
                
                breakdown = self.calculator.get_full_score(metrics)
                
                # 3. Update DB
                topic.viral_score = breakdown.viral_total
                topic.engagement_score = breakdown.engagement
                topic.emotional_score = breakdown.emotional
                topic.recency_score = breakdown.recency
                topic.ranking_metadata = breakdown.metadata
                topic.ranking_updated_at = datetime.utcnow()
                
            await session.commit()
            log.info("✅ Trend analysis and ranking completed")
