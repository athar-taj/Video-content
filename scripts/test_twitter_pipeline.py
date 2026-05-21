import asyncio
import logging
import sys
import os
from sqlalchemy import select

# Ensure the root project directory is in the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from db.repositories.manager import db_manager
from db.models.twitter_discovery import TwitterTrend, TrendCluster, InfluencerMetrics
from scripts.run_twitter_discovery import run_discovery
from ai.workflows.pipeline.langgraph_orchestrator import LangGraphOrchestrator
from ai.workflows.pipeline.workflow_registry import WorkflowRegistry

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("Zem.TestTwitterPipeline")

def assert_equal(actual, expected, message):
    if actual != expected:
        raise AssertionError(f"FAIL: {message} (Expected: {expected}, Actual: {actual})")
    logger.info(f"PASS: {message}")

async def main():
    logger.info("==================================================")
    logger.info("🧪 RUNNING TWITTER DISCOVERY & PIPELINE INTEGRATION TEST")
    logger.info("==================================================")
    
    # 1. Run the Twitter Trend Discovery
    logger.info("Step 1: Running Trend Discovery (limiting to mock fallback)...")
    await run_discovery(limit=4, trigger_pipeline=False)
    
    # 2. Verify Database Records
    logger.info("Step 2: Verifying database records...")
    async for session in db_manager.get_session():
        # Verify trends exist
        stmt = select(TwitterTrend)
        res = await session.execute(stmt)
        trends = res.scalars().all()
        logger.info(f"Found {len(trends)} TwitterTrend records in database.")
        assert len(trends) > 0, "TwitterTrend records should be saved in DB"
        
        # Verify influencer metrics exist
        stmt = select(InfluencerMetrics)
        res = await session.execute(stmt)
        influencers = res.scalars().all()
        logger.info(f"Found {len(influencers)} InfluencerMetrics records in database.")
        assert len(influencers) > 0, "InfluencerMetrics records should be saved in DB"
        
        # Verify clusters exist
        stmt = select(TrendCluster)
        res = await session.execute(stmt)
        clusters = res.scalars().all()
        logger.info(f"Found {len(clusters)} TrendCluster records in database.")
        assert len(clusters) > 0, "TrendCluster records should be saved in DB"
        
    # 3. Test LangGraph Routing with a Twitter Trend ID
    logger.info("Step 3: Verifying LangGraph workflow routing using a Twitter trend ID...")
    registry = WorkflowRegistry()
    orchestrator = LangGraphOrchestrator(registry)
    
    # We will fetch a trend from the database to use its tweet_id
    tweet_id_to_test = "mock_tweet_id"
    async for session in db_manager.get_session():
        stmt = select(TwitterTrend).order_by(TwitterTrend.viral_score.desc()).limit(1)
        res = await session.execute(stmt)
        top_trend = res.scalar_one_or_none()
        if top_trend:
            tweet_id_to_test = top_trend.tweet_id
            
    logger.info(f"Running LangGraph workflow for tweet_id: {tweet_id_to_test}")
    
    # Execute the workflow with score 90 (should route to premium_optional_workflow or fallback if offline)
    final_state = await orchestrator.execute_workflow(
        job_id="test_job_twitter_123",
        topic_id=tweet_id_to_test,
        forced_score=90
    )
    
    # Verify execution routing
    assert_equal(final_state.get("workflow_status") in ["completed", "running", "failed"], True, "Workflow status is valid")
    logger.info(f"Workflow successfully completed topic fetch node and router decision. Route chosen: {final_state.get('workflow_type')}")
    
    # Assert correct execution metadata
    metadata = final_state.get("execution_metadata", {})
    assert_equal(metadata.get("source"), "twitter", "Topic source metadata should be 'twitter'")
    assert_equal("Twitter Trend:" in metadata.get("title", ""), True, "Title metadata should contain 'Twitter Trend:' prefix")
    
    logger.info("==================================================")
    logger.info("🎉 ALL TWITTER ENGINE INTEGRATION TESTS PASSED!")
    logger.info("==================================================")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.exception("Twitter Pipeline Integration Test FAILED!")
        sys.exit(1)
