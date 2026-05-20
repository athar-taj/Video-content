import asyncio
from ai.discovery.reddit.trend_analyzer import TrendAnalyzer
from shared.redis.client import redis_manager
from shared.logging.logger import log

async def main():
    log.info("🚀 Launching Trend Ranking Pipeline")
    
    # 1. Init Redis
    await redis_manager.connect()
    
    # 2. Run Analyzer
    analyzer = TrendAnalyzer()
    try:
        await analyzer.analyze_and_rank()
    except Exception as e:
        log.exception(f"Fatal error in trend ranking: {e}")
    finally:
        await redis_manager.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
