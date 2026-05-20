import asyncpraw
from typing import List, Dict, Any
from ai.discovery.reddit.client import reddit_client
from shared.config.settings import settings
from shared.logging.logger import log

class RedditFetcher:
    """Handles fetching posts and comments from specific subreddits."""
    
    def __init__(self, limit: int = 10):
        self.limit = limit or settings.FETCH_LIMIT

    async def fetch_posts(self, subreddit_name: str, sort: str = "hot") -> List[Dict[str, Any]]:
        """Fetch posts from a subreddit."""
        reddit = await reddit_client.get_instance()
        subreddit = await reddit.subreddit(subreddit_name)
        
        posts = []
        log.info(f"Fetching {self.limit} {sort} posts from r/{subreddit_name}")
        
        iterator = getattr(subreddit, sort)(limit=self.limit)
        async for submission in iterator:
            posts.append({
                "reddit_id": submission.id,
                "title": submission.title,
                "body": submission.selftext,
                "author": str(submission.author),
                "score": submission.score,
                "comments_count": submission.num_comments,
                "permalink": submission.permalink,
                "is_nsfw": submission.over_18,
                "created_utc": submission.created_utc,
                "flair": submission.link_flair_text,
                "upvotes": submission.ups
            })
            
        return posts

    async def fetch_comments(self, submission_id: str, depth: int = 1, limit: int = 5) -> List[Dict[str, Any]]:
        """Fetch top comments for a specific post."""
        reddit = await reddit_client.get_instance()
        submission = await reddit.submission(id=submission_id)
        
        submission.comment_sort = "top"
        await submission.comments.replace_more(limit=0) # Only fetch top-level comments for now
        
        comments = []
        for comment in submission.comments[:limit]:
            if str(comment.author).lower() in ["automoderator", "deleted"]:
                continue
                
            comments.append({
                "comment_body": comment.body,
                "score": comment.score,
                "author": str(comment.author),
                "replies_count": len(comment.replies)
            })
            
        return comments
