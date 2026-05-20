from typing import List, Dict, Any
import hashlib
from ai.discovery.reddit.fetcher import RedditFetcher
from ai.discovery.reddit.filters import RedditFilters
from ai.discovery.reddit.cleaner import TextCleaner
from ai.discovery.reddit.filters import ViralRanking as ViralScorer
from ai.discovery.reddit.duplicate_detector import DuplicateDetector
from db.repositories.manager import db_manager
from db.repositories.discovery_repo import DiscoveryRepository
from shared.logging.logger import log
from shared.config.settings import settings

class RedditDiscoveryPipeline:
    """Orchestrates the entire Reddit ingestion process."""
    
    def __init__(self):
        self.fetcher = RedditFetcher()
        self.cleaner = TextCleaner()

    def _generate_hash(self, text: str) -> str:
        return hashlib.sha256(text.lower().encode()).hexdigest()

    async def run(self, subreddits: List[str] = None):
        subs = subreddits or settings.TARGET_SUBREDDITS
        log.info(f"🚀 Starting Reddit Discovery Pipeline for {len(subs)} subreddits")
        
        async for session in db_manager.get_session():
            repo = DiscoveryRepository(session)
            
            for sub in subs:
                try:
                    # 1. Fetch
                    posts = await self.fetcher.fetch_posts(sub)
                    
                    for post in posts:
                        # 2. Duplicate Check (Hash based)
                        content_hash = self._generate_hash(post["title"])
                        if await repo.topic_exists(post["reddit_id"]) or await DuplicateDetector.is_duplicate_in_cache(content_hash):
                            log.debug(f"Skipping duplicate: {post['reddit_id']}")
                            continue
                            
                        # 3. Quality Filter
                        if not RedditFilters.is_quality_post(post):
                            continue
                            
                        # 4. Clean Content
                        post["title"] = self.cleaner.clean_reddit_text(post["title"])
                        post["body"] = self.cleaner.clean_reddit_text(post["body"])
                        post["subreddit"] = sub
                        
                        # 5. Viral Score (Initial)
                        post["viral_score"] = ViralScorer.calculate_score(post)
                        
                        # 6. Fetch Comments
                        comments = await self.fetcher.fetch_comments(post["reddit_id"])
                        for c in comments:
                            c["comment_body"] = self.cleaner.clean_reddit_text(c["comment_body"])
                            
                        # 7. Store
                        topic_obj = await repo.save_reddit_topic(post)
                        await repo.save_reddit_comments(topic_obj.id, comments)
                        
                        # Mark as seen in Redis
                        await DuplicateDetector.mark_as_seen(content_hash)
                        
                        log.info(f"✅ Ingested: {post['title'][:50]}... (Score: {post['viral_score']})")
                        
                except Exception as e:
                    log.error(f"Error processing r/{sub}: {e}")
                    continue
                    
        log.info("🏁 Reddit Discovery Pipeline finished")
