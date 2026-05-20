import asyncio
import argparse
from ai.discovery.pipeline.orchestrator import ContentDiscoveryOrchestrator
from ai.discovery.reddit.client import reddit_client
from shared.logging.logger import log

async def main():
    parser = argparse.ArgumentParser(description="Zem Unified Content Discovery Pipeline")
    parser.add_argument("--subreddits", type=str, help="Comma-separated list of subreddits to ingest")
    parser.add_argument("--limit", type=int, default=25, help="Number of posts to fetch per subreddit")
    args = parser.parse_args()

    log.info("🌟 Starting Unified Content Discovery Execution")
    
    # 1. Initialize Orchestrator
    orchestrator = ContentDiscoveryOrchestrator()
    
    # 2. Parse Subreddits
    target_subs = None
    if args.subreddits:
        target_subs = [s.strip() for s in args.subreddits.split(",")]

    # 3. RUN PIPELINE
    try:
        await orchestrator.run(subreddits=target_subs)
    except Exception as e:
        log.error(f"Execution failed: {e}")
    finally:
        # Ensure Reddit client is closed
        await reddit_client.close()
        log.info("👋 Discovery Pipeline execution finished")

if __name__ == "__main__":
    asyncio.run(main())
