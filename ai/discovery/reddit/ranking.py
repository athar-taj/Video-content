import math
import time
from typing import Dict, Any
from ai.discovery.reddit.scoring_models import TrendMetrics, ScoreBreakdown
from shared.config.settings import settings

class ViralScoreCalculator:
    """Calculates multidimensional viral scores for topics."""
    
    @staticmethod
    def calculate_engagement_score(metrics: TrendMetrics) -> float:
        # Logarithmic scaling for high volumes
        log_upvotes = math.log1p(metrics.upvotes)
        log_comments = math.log1p(metrics.comments_count * 2) # Comments are more valuable for retention
        
        raw_score = (log_upvotes * settings.UPVOTES_WEIGHT) + (log_comments * settings.COMMENTS_WEIGHT)
        return float(round(raw_score * 10, 2))

    @staticmethod
    def calculate_recency_score(metrics: TrendMetrics) -> float:
        # Time decay: Exponential decay based on hours
        now = time.time()
        age_hours = (now - metrics.created_utc) / 3600
        
        # Half-life of 24 hours
        halflife = 24
        decay = math.exp(-math.log(2) * age_hours / halflife)
        
        return float(round(decay * 100, 2))

    @staticmethod
    def calculate_emotional_score(title: str) -> float:
        # Simple keyword-based detection for now
        triggers = {
            "shock": ["shocking", "unbelievable", "never thought", "omg"],
            "suspense": ["secret", "hidden", "revealed", "truth"],
            "conflict": ["ruined", "cheated", "betrayed", "fight", "clash"],
            "curiosity": ["what happened", "why", "how I", "story of"]
        }
        
        score = 0.0
        title_lower = title.lower()
        for category, words in triggers.items():
            if any(word in title_lower for word in words):
                score += 2.5 # Max 10 if all categories hit (unlikely)
        
        return min(score, 10.0)

    def get_full_score(self, metrics: TrendMetrics) -> ScoreBreakdown:
        engagement = self.calculate_engagement_score(metrics)
        recency = self.calculate_recency_score(metrics)
        emotional = self.calculate_emotional_score(metrics.title)
        
        # Combine using weights
        # Recency acts as a multiplier to the viral potential
        total = (engagement + emotional) * (recency / 100)
        
        return ScoreBreakdown(
            engagement=engagement,
            recency=recency,
            emotional=emotional,
            viral_total=float(round(total, 2)),
            metadata={
                "age_hours": round((time.time() - metrics.created_utc) / 3600, 1)
            }
        )
