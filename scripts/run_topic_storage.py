import asyncio
from ai.discovery.storage.topic_storage import TopicStorageService
from shared.logging.logger import log

async def main():
    log.info("🚀 Launching Topic Storage Pipeline")
    
    # This is a demonstration script that would normally be part of the Reddit pipeline
    storage = TopicStorageService()
    
    # Simulated topics
    sample_topics = [
        {
            "reddit_id": "test1",
            "subreddit": "AskReddit",
            "title": "What is the most mysterious thing that happened to you?",
            "body": "Tell your story...",
            "author": "user1",
            "score": 1000,
            "comments_count": 500,
            "created_utc": 1620000000,
            "permalink": "/r/AskReddit/comments/test1",
            "is_nsfw": False
        }
    ]
    
    try:
        await storage.store_batch(sample_topics)
        log.info("✅ Storage task completed")
    except Exception as e:
        log.error(f"Storage pipeline error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
