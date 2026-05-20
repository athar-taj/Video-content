import re
from typing import List, Tuple

class ProfanityFilter:
    """Detects abusive language and monetization-risk words."""
    
    # Example blocklist (in production, this would be much larger)
    DEFAULT_BLOCKLIST = [
        r"\b(fuck|shit|asshole|bitch|bastard)\b",
        r"\b(kill|suicide|murder|violent|death)\b" # Monetization risk
    ]

    def __init__(self, blocklist: List[str] = None):
        self.blocklist = blocklist or self.DEFAULT_BLOCKLIST

    def analyze(self, text: str) -> Tuple[float, List[str]]:
        """
        Returns a profanity score (0-1, where 0 is clean) 
        and a list of matches.
        """
        if not text:
            return 0.0, []
            
        matches = []
        text_lower = text.lower()
        
        for pattern in self.blocklist:
            found = re.findall(pattern, text_lower)
            if found:
                matches.extend(found)
        
        # Calculate score: percentage of "bad" words relative to length
        word_count = len(text.split())
        score = len(matches) / word_count if word_count > 0 else 0
        
        return min(score * 10, 1.0), list(set(matches))
