import asyncio
import logging
import sys
import os
import argparse

# Ensure the root project directory is in the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts.run_twitter_discovery import run_discovery

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("Zem.MonitorTwitterTrends")

async def main():
    parser = argparse.ArgumentParser(description="Zem Twitter Trends Monitor Service")
    parser.add_argument("--interval", type=int, default=3600, help="Interval in seconds between trend checks")
    parser.add_argument("--limit", type=int, default=15, help="Number of trends to fetch per cycle")
    args = parser.parse_args()

    logger.info("==================================================")
    logger.info("📡 TWITTER TREND MONITOR SERVICE INITIALIZED")
    logger.info(f"Checking every {args.interval} seconds (Limit: {args.limit} tweets)")
    logger.info("==================================================")

    try:
        while True:
            logger.info("Starting monitoring check cycle...")
            try:
                # Execute discovery
                await run_discovery(limit=args.limit, trigger_pipeline=False)
                logger.info("Monitoring check cycle finished successfully.")
            except Exception as inner_e:
                logger.error(f"Error during trend monitoring cycle: {inner_e}", exc_info=True)
            
            logger.info(f"Sleeping for {args.interval} seconds before next cycle...")
            await asyncio.sleep(args.interval)
            
    except asyncio.CancelledError:
        logger.info("Monitor service shutdown requested.")
    except Exception as e:
        logger.critical(f"Monitor service crashed: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Monitor service stopped by user.")
