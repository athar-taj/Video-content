import time
import hashlib
from typing import List, Dict, Any
from ai.discovery.reddit.fetcher import RedditFetcher
from ai.discovery.reddit.filters import RedditFilters, ViralRanking
from ai.discovery.reddit.cleaner import TextCleaner
from ai.discovery.reddit.duplicate_detector import DuplicateDetector
from ai.discovery.storage.topic_storage import TopicStorageService
from ai.discovery.pipeline.pipeline_state import DiscoveryState
from db.repositories.manager import db_manager
from db.repositories.topic_repository import TopicRepository
from shared.redis.client import redis_manager
from shared.logging.logger import log
from shared.config.settings import settings

class ContentDiscoveryOrchestrator:
    """Master orchestrator for the Phase 1 Content Discovery pipeline."""
    
    def __init__(self):
        self.fetcher = RedditFetcher(limit=settings.FETCH_LIMIT)
        self.cleaner = TextCleaner()
        self.storage = TopicStorageService()
        self.state = DiscoveryState()

    def _generate_hash(self, text: str) -> str:
        return hashlib.sha256(text.lower().encode()).hexdigest()

    async def run(self, subreddits: List[str] = None):
        """Execute the full end-to-end discovery flow."""
        start_time = time.time()
        subs = subreddits or settings.TARGET_SUBREDDITS
        
        log.info(f"🚀 Initializing Content Discovery Orchestrator for {len(subs)} subreddits")
        self.state.current_stage = "fetching"

        try:
            # Connect to necessary infrastructure
            await redis_manager.connect()
            
            async with db_manager.get_session() as session:
                repo = TopicRepository(session)
                
                for sub in subs:
                    try:
                        log.info(f"📂 Processing r/{sub}...")
                        
                        # 1. FETCH
                        posts = await self.fetcher.fetch_posts(sub)
                        self.state.update_metrics(total_fetched=len(posts))
                        
                        for post in posts:
                            # 2. DUPLICATE CHECK (L1: Reddit ID)
                            if await repo.get_by_reddit_id(post["reddit_id"]):
                                self.state.update_metrics(total_duplicates=1)
                                continue
                                
                            # 3. DUPLICATE CHECK (L2: Content Hash via Redis)
                            content_hash = self._generate_hash(post["title"])
                            if await DuplicateDetector.is_duplicate_in_cache(content_hash):
                                self.state.update_metrics(total_duplicates=1)
                                continue
                                
                            # 4. QUALITY FILTER
                            if not RedditFilters.is_quality_post(post):
                                self.state.update_metrics(total_filtered=1)
                                continue
                                
                            # 5. CLEAN CONTENT
                            post["title"] = self.cleaner.clean_reddit_text(post["title"])
                            post["body"] = self.cleaner.clean_reddit_text(post["body"])
                            post["subreddit"] = sub
                            post["content_hash"] = content_hash
                            
                            # 6. INITIAL VIRAL SCORING
                            post["viral_score"] = ViralRanking.calculate_score(post)
                            
                            # 7. COMMENT EXTRACTION
                            comments = await self.fetcher.fetch_comments(post["reddit_id"])
                            self.state.update_metrics(total_comments=len(comments))
                            
                            # 8. STORAGE & WORKFLOW TRACKING
                            # The storage service handles topic + comments + initial status
                            topic_obj = await repo.create(post)
                            # Log initial stage
                            log.debug(f"Saved topic {topic_obj.id} to database")
                            
                            # 9. MARK AS SEEN
                            await DuplicateDetector.mark_as_seen(content_hash)
                            self.state.update_metrics(total_stored=1)
                            
                        await session.commit()
                        
                    except Exception as e:
                        error_msg = f"Error in subreddit {sub}: {str(e)}"
                        log.error(error_msg)
                        self.state.log_error(error_msg)
                        continue

            self.state.is_complete = True
            self.state.current_stage = "completed"
            
        except Exception as e:
            self.state.current_stage = "failed"
            log.exception(f"Critical failure in Discovery Orchestrator: {e}")
            raise
        finally:
            self.state.metrics.duration_ms = (time.time() - start_time) * 1000
            await redis_manager.disconnect()
            self._print_summary()

    def _print_summary(self):
        m = self.state.metrics
        log.info("="*50)
        log.info("🏁 CONTENT DISCOVERY PIPELINE SUMMARY")
        log.info("="*50)
        log.info(f"Total Fetched:    {m.total_fetched}")
        log.info(f"Total Filtered:   {m.total_filtered}")
        log.info(f"Total Duplicates: {m.total_duplicates}")
        log.info(f"Total Stored:     {m.total_stored}")
        log.info(f"Total Duration:   {m.duration_ms:.2f}ms")
        log.info(f"Status:           {self.state.current_stage.upper()}")
        log.info("="*50)
