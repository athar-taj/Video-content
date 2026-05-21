import asyncio
import argparse
import sys
import os

# Ensure the root project directory is in the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ai.discovery.reddit.pipeline import RedditDiscoveryPipeline
from ai.discovery.reddit.client import reddit_client
from shared.logging.logger import log

async def main():
    # Pre-flight health checks
    from shared.validation.environment_validator import EnvironmentValidator
    validator = EnvironmentValidator()
    if not await validator.generate_health_report():
        log.critical("Pre-flight check failed. Aborting Reddit discovery.")
        sys.exit(1)

    parser = argparse.ArgumentParser(description="Zem Reddit Discovery Pipeline")
    parser.add_argument("--subreddits", type=str, help="Comma-separated subreddits to fetch")
    args = parser.parse_args()

    # 1. Initialize Pipeline
    pipeline = RedditDiscoveryPipeline()
    
    # 2. Parse Subreddits
    target_subs = None
    if args.subreddits:
        target_subs = [s.strip() for s in args.subreddits.split(",")]

    # 3. Execute
    try:
        await pipeline.run(subreddits=target_subs)
    except Exception as e:
        log.exception(f"Fatal pipeline error: {e}")
    finally:
        await reddit_client.close()

if __name__ == "__main__":
    asyncio.run(main())
