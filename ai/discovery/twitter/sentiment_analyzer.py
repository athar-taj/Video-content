import logging

logger = logging.getLogger("Zem.SentimentAnalyzer")

class SentimentAnalyzer:
    """Classifies sentiment polarity of social text content."""
    
    POSITIVE_WORDS = ["love", "best", "great", "win", "genius", "amazing", "incredible", "success", "future"]
    NEGATIVE_WORDS = ["fail", "terrible", "worst", "ruin", "furious", "hate", "bad", "loss", "danger", "warning"]

    def analyze_sentiment(self, text: str) -> str:
        content = text.lower()
        pos_count = sum(1 for w in self.POSITIVE_WORDS if w in content)
        neg_count = sum(1 for w in self.NEGATIVE_WORDS if w in content)
        
        if pos_count > neg_count:
            return "positive"
        elif neg_count > pos_count:
            return "negative"
        else:
            return "neutral"
