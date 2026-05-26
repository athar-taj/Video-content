import hashlib
import time
from typing import List, Dict, Any
from db.repositories.topic_repository import TopicRepository
from db.repositories.manager import db_manager
from shared.logging.logger import log
from shared.redis.client import redis_manager

class TopicStorageService:
    """Orchestrates the validation, hashing, and storage of topics."""
    
    @staticmethod
    def generate_content_hash(title: str, body: str = "") -> str:
        """Generate a deterministic fingerprint for content."""
        normalized = f"{title.lower().strip()}|{body.lower().strip()[:200]}"
        return hashlib.sha256(normalized.encode()).hexdigest()

    async def store_batch(self, topics: List[Dict[str, Any]]):
        """Process and store a batch of topics with duplicate prevention."""
        async with db_manager.get_session() as session:
            repo = TopicRepository(session)
            
            for topic_data in topics:
                try:
                    # 1. Hashing
                    c_hash = self.generate_content_hash(topic_data["title"], topic_data.get("body", ""))
                    topic_data["content_hash"] = c_hash
                    
                    # 2. Duplicate Check (DB + Redis)
                    if await repo.get_by_reddit_id(topic_data["reddit_id"]):
                        continue
                        
                    # 3. Store
                    topic_obj = await repo.create(topic_data)
                    log.info(f"Stored topic: {topic_obj.id} | {topic_obj.title[:30]}")
                    
                except Exception as e:
                    log.error(f"Failed to store topic {topic_data.get('reddit_id')}: {e}")
                    await session.rollback()
                    continue
                    
            await session.commit()
