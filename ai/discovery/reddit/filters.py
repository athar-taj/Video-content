from typing import Dict, Any
from shared.logging.logger import log

class RedditFilters:
    """Filters for quality and safety."""
    
    @staticmethod
    def is_quality_post(post: Dict[str, Any]) -> bool:
        # 1. NSFW Check
        if post.get("is_nsfw"):
            log.debug(f"Filtered NSFW post: {post['reddit_id']}")
            return False
            
        # 2. Length Check (for story-based subreddits)
        body_len = len(post.get("body", ""))
        if body_len < 100:
            log.debug(f"Filtered short post: {post['reddit_id']}")
            return False
            
        # 3. Minimum Engagement
        if post.get("score", 0) < 50:
            log.debug(f"Filtered low score post: {post['reddit_id']}")
            return False
            
        return True

class ViralRanking:
    """Algorithm to calculate viral potential."""
    
    @staticmethod
    def calculate_score(post: Dict[str, Any]) -> float:
        upvotes = post.get("upvotes", 0)
        comments = post.get("comments_count", 0)
        
        # Simple weighted score
        # upvotes * 0.4 + comments * 0.3 + baseline
        score = (upvotes * 0.4) + (comments * 0.6)
        
        # Penalty for extreme length or very short (optional)
        return float(round(score, 2))
