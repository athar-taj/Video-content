import re
import html

class TextCleaner:
    """Utilities for cleaning and normalizing Reddit text."""
    
    @staticmethod
    def clean_reddit_text(text: str) -> str:
        if not text:
            return ""
            
        # 1. Unescape HTML entities
        text = html.unescape(text)
        
        # 2. Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        
        # 3. Remove Markdown artifacts (simple)
        text = re.sub(r'[\*\_~`\[\]\(\)]', '', text)
        
        # 4. Remove common Reddit noise (Edit:, Update:, etc.)
        text = re.sub(r'(?i)edit:.*|(?i)update:.*', '', text)
        
        # 5. Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
