import re
import logging
from typing import List, Set, Dict
from ai.discovery.twitter.models import TweetModel, TrendClusterModel

logger = logging.getLogger("Zem.TopicClusterer")

class TopicClusterer:
    """
    Groups similar tweets into semantic topic clusters using keyword/token overlap.
    Reduces redundant duplicate trends.
    """

    def _get_tokenize_words(self, text: str) -> Set[str]:
        """Normalize and tokenize text into unique words of length > 3."""
        clean_text = re.sub(r"[^\w\s]", "", text.lower())
        words = clean_text.split()
        return {w for w in words if len(w) > 3}

    def calculate_similarity(self, t1: TweetModel, t2: TweetModel) -> float:
        """Calculate Jaccard similarity score between two tweets based on token words and hashtags."""
        words1 = self._get_tokenize_words(t1.content)
        words2 = self._get_tokenize_words(t2.content)
        
        # Add hashtags to the word pool
        words1.update(h.lower() for h in t1.hashtags)
        words2.update(h.lower() for h in t2.hashtags)
        
        if not words1 or not words2:
            return 0.0
            
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)

    def cluster_tweets(self, tweets: List[TweetModel], threshold: float = 0.15) -> List[TrendClusterModel]:
        """Cluster list of tweets into topic clusters."""
        clusters: List[TrendClusterModel] = []
        
        for tweet in tweets:
            matched_cluster = None
            
            # Find if this tweet belongs to any existing cluster
            for cluster in clusters:
                # Compare against all tweets in the cluster
                similarities = [self.calculate_similarity(tweet, ct) for ct in cluster.tweets]
                max_sim = max(similarities) if similarities else 0.0
                
                if max_sim >= threshold:
                    matched_cluster = cluster
                    break
            
            if matched_cluster:
                matched_cluster.tweets.append(tweet)
            else:
                # Create a new cluster
                # Use primary hashtags or the first few words as cluster name
                tags = [f"#{t}" for t in tweet.hashtags[:2]]
                cluster_name = " ".join(tags) if tags else " ".join(tweet.content.split()[:4]) + "..."
                
                new_cluster = TrendClusterModel(
                    cluster_name=cluster_name,
                    cluster_score=tweet.viral_score,
                    tweets=[tweet]
                )
                clusters.append(new_cluster)

        # Update scores based on aggregate metrics
        for cluster in clusters:
            if cluster.tweets:
                # Average viral score weighted slightly by number of tweets in cluster
                avg_score = sum(t.viral_score for t in cluster.tweets) / len(cluster.tweets)
                bonus = min(len(cluster.tweets) * 5.0, 20.0) # Bonus for cluster size
                cluster.cluster_score = round(min(avg_score + bonus, 100.0), 2)
                
                # Update cluster name to be the most active tweet's hook if default
                top_tweet = max(cluster.tweets, key=lambda t: t.viral_score)
                if top_tweet.hook:
                    cluster.cluster_name = top_tweet.hook
                    
        # Sort clusters by score
        clusters.sort(key=lambda c: c.cluster_score, reverse=True)
        logger.info(f"Clustered {len(tweets)} tweets into {len(clusters)} narrative topics.")
        
        return clusters
