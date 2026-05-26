import asyncio
import logging
import sys
import os
import hashlib
from datetime import datetime

# Ensure the root project directory is in the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from shared.validation.environment_validator import EnvironmentValidator
from ai.discovery.twitter.fallback_router import TwitterFallbackRouter
from ai.discovery.twitter.trend_detector import TrendDetector
from ai.discovery.twitter.virality_analyzer import ViralityAnalyzer
from ai.discovery.twitter.topic_clusterer import TopicClusterer
from ai.discovery.twitter.influencer_detector import InfluencerDetector
from db.repositories.manager import db_manager
from db.models.twitter_discovery import TwitterTrend, TrendCluster, InfluencerMetrics
from sqlalchemy import select

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("Zem.RunTwitterDiscovery")

async def run_discovery(limit: int = 15, trigger_pipeline: bool = False):
    logger.info("==================================================")
    logger.info("🎬 STARTING REAL-TIME X/TWITTER TREND DISCOVERY")
    logger.info("==================================================")
    
    # 1. Pre-flight check
    validator = EnvironmentValidator()
    if not await validator.generate_health_report():
        logger.critical("Pre-flight environment validation failed. Aborting Twitter Discovery.")
        sys.exit(1)
        
    # 2. Ingest trends via Router (API v2 -> Scraper -> Mock fallback)
    router = TwitterFallbackRouter()
    logger.info("Ingesting raw trends...")
    raw_tweets = await router.fetch_trends(limit=limit)
    
    if not raw_tweets:
        logger.warning("No trends fetched. Exiting.")
        return
        
    # 3. Analyze Trend & Virality
    trend_detector = TrendDetector()
    virality_analyzer = ViralityAnalyzer()
    
    logger.info("Analyzing and scoring tweet virality metrics...")
    scored_tweets = []
    for t in raw_tweets:
        # Calculate velocity
        velocity = trend_detector.calculate_velocity(t)
        t.engagement_score = velocity
        
        # Analyze emotion, hook, and final viral score
        analyzed = virality_analyzer.analyze_virality(t)
        
        # Rule: viral_score < 40 gets discarded
        if analyzed.viral_score < 40:
            logger.info(f"Discarding tweet {t.tweet_id} (Score: {analyzed.viral_score} < 40)")
            continue
            
        scored_tweets.append(analyzed)
        
    logger.info(f"Retained {len(scored_tweets)} / {len(raw_tweets)} tweets above viral threshold (>= 40).")
    if not scored_tweets:
        logger.info("No tweets met the virality criteria. Exiting.")
        return
        
    # 4. Cluster Topics
    logger.info("Clustering trends into narrative topics...")
    clusterer = TopicClusterer()
    clusters = clusterer.cluster_tweets(scored_tweets)
    logger.info(f"Formed {len(clusters)} narrative clusters.")
    
    # 5. Persist to Database
    logger.info("Persisting results to database...")
    async with db_manager.get_session() as session:
        # Store Trends
        for tweet in scored_tweets:
            # Check for existing tweet
            stmt = select(TwitterTrend).where(TwitterTrend.tweet_id == tweet.tweet_id)
            res = await session.execute(stmt)
            existing = res.scalar_one_or_none()
            
            content_hash = hashlib.sha256(tweet.content.encode('utf-8')).hexdigest()
            
            if not existing:
                db_trend = TwitterTrend(
                    tweet_id=tweet.tweet_id,
                    author=tweet.author,
                    content=tweet.content,
                    hashtags={"tags": tweet.hashtags},
                    engagement_score=tweet.engagement_score,
                    viral_score=tweet.viral_score,
                    emotional_score=tweet.emotional_score,
                    retention_score=tweet.retention_score,
                    content_hash=content_hash,
                    processing_status="fetched",
                    processing_stage="discovery"
                )
                session.add(db_trend)
                logger.info(f"Saved new trend: @{tweet.author} - Viral Score: {tweet.viral_score}")
            else:
                existing.engagement_score = tweet.engagement_score
                existing.viral_score = tweet.viral_score
                existing.emotional_score = tweet.emotional_score
                existing.retention_score = tweet.retention_score
                existing.updated_at = datetime.utcnow()
                logger.info(f"Updated existing trend: @{tweet.author} (ID: {tweet.tweet_id})")
                
            # Store/Update Influencer metrics
            influencer = InfluencerDetector.analyze_author_tweet(tweet.author, tweet.likes, tweet.retweets)
            stmt = select(InfluencerMetrics).where(InfluencerMetrics.username == tweet.author)
            res = await session.execute(stmt)
            existing_inf = res.scalar_one_or_none()
            
            if not existing_inf:
                db_inf = InfluencerMetrics(
                    username=tweet.author,
                    influence_score=influencer.influence_score,
                    engagement_rate=influencer.engagement_rate
                )
                session.add(db_inf)
            else:
                existing_inf.influence_score = influencer.influence_score
                existing_inf.engagement_rate = influencer.engagement_rate
                
        # Store Clusters
        for c in clusters:
            db_cluster = TrendCluster(
                cluster_name=c.cluster_name,
                cluster_score=c.cluster_score
            )
            session.add(db_cluster)
            
        await session.commit()
        logger.info("Database sync complete.")
        
    # 6. Trigger LangGraph Pipeline (Optional)
    if trigger_pipeline:
        # Sort and get highest score
        top_trend = sorted(scored_tweets, key=lambda x: x.viral_score, reverse=True)[0]
        logger.info(f"Triggering video production pipeline for highest viral trend: {top_trend.tweet_id} (Score: {top_trend.viral_score})")
        
        from ai.workflows.pipeline.langgraph_orchestrator import LangGraphOrchestrator
        from ai.workflows.pipeline.workflow_registry import WorkflowRegistry
        import uuid
        
        registry = WorkflowRegistry()
        orchestrator = LangGraphOrchestrator(registry)
        
        job_id = f"job_twitter_{uuid.uuid4().hex[:8]}"
        
        # Run orchestrator
        final_state = await orchestrator.execute_workflow(
            job_id=job_id,
            topic_id=top_trend.tweet_id,
            forced_score=top_trend.viral_score
        )
        logger.info(f"Pipeline executed. Status: {final_state.get('workflow_status')}")

if __name__ == "__main__":
    trigger = "--trigger" in sys.argv
    asyncio.run(run_discovery(limit=10, trigger_pipeline=trigger))
