import re
import logging
from typing import Dict, Any
from ai.discovery.twitter.models import TweetModel

logger = logging.getLogger("Zem.ViralityAnalyzer")

class ViralityAnalyzer:
    """
    Analyzes emotional intensity, hooks, controversy, and storytelling markers in tweets.
    Computes LangGraph-compatible virality scores.
    """

    # Hook patterns for shorts/reels retention
    HOOK_PATTERNS = [
        r"nobody saw this coming",
        r"this changed everything",
        r"the internet is exploding",
        r"you won't believe",
        r"crazy story",
        r"unbelievable",
        r"the truth about",
        r"why everyone is",
        r"secret to",
        r"stop doing"
    ]

    # Emotional intensity trigger words
    EMOTION_KEYWORDS = [
        "shock", "insane", "furious", "ruined", "exposing", "cheat", "brutal", "incredible",
        "worst", "best", "failed", "broke", "genius", "crazy", "exploding", "secret", "exposed"
    ]

    def analyze_emotional_score(self, content: str) -> float:
        """Rate emotional intensity on a scale of 0 to 100."""
        text = content.lower()
        score = 20.0 # Base score
        
        # 1. Punctuation checks
        exclamations = len(re.findall(r"!", text))
        questions = len(re.findall(r"\?", text))
        score += min(exclamations * 10, 30)
        score += min(questions * 5, 15)

        # 2. Key phrase checks
        matches = sum(1 for word in self.EMOTION_KEYWORDS if word in text)
        score += min(matches * 15, 35)

        # 3. Capitalization check (SHOUTING)
        shout_words = len([w for w in content.split() if w.isupper() and len(w) > 2])
        if shout_words > 0:
            score += min(shout_words * 5, 20)

        return min(round(score, 2), 100.0)

    def analyze_retention_score(self, content: str) -> float:
        """Rate hooks and curiosity loop potential for shorts (0 to 100)."""
        text = content.lower()
        score = 30.0 # Base score

        # Check for listicles (e.g. "1.", "3 ways", "5 tools")
        if re.search(r"\b\d+\s+(ways|tools|steps|secrets|tips|reasons)\b", text) or re.search(r"^\d+\.", text, re.MULTILINE):
            score += 25.0

        # Check for known viral hooks
        for pattern in self.HOOK_PATTERNS:
            if re.search(pattern, text):
                score += 30.0
                break

        # Check for paragraph structure/breaks (good for script building)
        if len(content.split("\n")) > 1:
            score += 15.0

        return min(round(score, 2), 100.0)

    def analyze_virality(self, tweet: TweetModel) -> TweetModel:
        """Perform full virality and sentiment analysis on a tweet model."""
        content = tweet.content
        
        # Compute scores
        emotion = self.analyze_emotional_score(content)
        retention = self.analyze_retention_score(content)
        
        # Calculate viral_score:
        # 40% Engagement Velocity + 30% Emotion + 30% Hook/Retention
        # Normalize engagement_score (maxed out at 1000 velocity)
        normalized_engagement = min((tweet.engagement_score / 1000.0) * 100.0, 100.0)
        
        viral_score = (normalized_engagement * 0.40) + (emotion * 0.30) + (retention * 0.30)
        
        # Assign back to model
        tweet.emotional_score = emotion
        tweet.retention_score = retention
        tweet.viral_score = min(round(viral_score, 2), 100.0)

        # Sentiment label fallback
        if emotion > 60:
            tweet.sentiment = "highly_charged"
        elif "failed" in content.lower() or "terrible" in content.lower():
            tweet.sentiment = "negative"
        elif "win" in content.lower() or "best" in content.lower():
            tweet.sentiment = "positive"
        else:
            tweet.sentiment = "neutral"

        # Auto-extract primary hook snippet
        sentences = content.split(".")
        if sentences:
            tweet.hook = sentences[0].strip()

        return tweet
