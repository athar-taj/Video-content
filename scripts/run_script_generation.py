import asyncio
import argparse
from ai.generation.script_generator.generator import ScriptGenerator
from db.repositories.manager import db_manager
from sqlalchemy import select
from db.models.reddit_topic import RedditTopic
from shared.logging.logger import log

async def main():
    parser = argparse.ArgumentParser(description="Zem Script Generation Pipeline")
    parser.add_argument("--limit", type=int, default=1, help="Number of scripts to generate")
    args = parser.parse_args()

    log.info("🚀 Launching Script Generation Pipeline")
    
    generator = ScriptGenerator()
    
    async with db_manager.get_session() as session:
        # 1. Fetch top ranked topics that don't have scripts yet
        stmt = select(RedditTopic).where(
            RedditTopic.processing_status == "fetched" # or "ranked"
        ).order_by(RedditTopic.viral_score.desc()).limit(args.limit)
        
        result = await session.execute(stmt)
        topics = result.scalars().all()
        
        if not topics:
            log.warning("No topics found for script generation.")
            return

        for topic in topics:
            try:
                # 2. Generate
                res = await generator.generate_full_script(
                    topic_id=topic.id,
                    title=topic.title,
                    raw_body=topic.body or "",
                    subreddit=topic.subreddit,
                    target_duration=60
                )
                
                print("\n" + "="*50)
                print(f"✨ SCRIPT FOR: {topic.title[:50]}...")
                print("="*50)
                print(f"HOOK: {res.hook}")
                print("-" * 20)
                print(f"FULL SCRIPT:\n{res.full_script}")
                print("="*50)
                print(f"ESTIMATED DURATION: {res.metadata['estimated_duration']:.2f}s")
                print("="*50 + "\n")
                
                # 3. Update Status
                topic.processing_status = "script_generated"
                
            except Exception as e:
                log.error(f"Failed to generate script for topic {topic.id}: {e}")
                
        await session.commit()

if __name__ == "__main__":
    asyncio.run(main())
