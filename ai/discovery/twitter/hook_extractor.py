import re
import logging
from typing import Optional

logger = logging.getLogger("Zem.HookExtractor")

class HookExtractor:
    """
    Extracts and refines attention-grabbing opening hooks from social content.
    Optimized for short-form video (Shorts, TikToks, Reels).
    """

    def clean_hook(self, text: str) -> str:
        """Clean emojis, hashtags, URLs, and formatting tags from the hook."""
        # Remove URLs
        clean = re.sub(r"https?://\S+", "", text)
        # Remove hashtags
        clean = re.sub(r"#\w+", "", clean)
        # Remove mentions
        clean = re.sub(r"@\w+", "", clean)
        # Remove brackets or formatting
        clean = re.sub(r"[\[\]\(\)\{\}]", "", clean)
        # Remove multiple whitespaces
        clean = re.sub(r"\s+", " ", clean).strip()
        return clean

    def extract_viral_hook(self, content: str) -> str:
        """Extract a single line hook suitable for a video opener."""
        # Split into sentences or lines
        lines = [line.strip() for line in re.split(r"[\n.!?]", content) if line.strip()]
        
        if not lines:
            return "Nobody saw this coming..."
            
        # Try to find a line matching viral hook style
        viral_markers = [
            "nobody", "never", "truth", "why", "secret", "exposed", "unbelievable", 
            "changed", "exploding", "shocking", "craziest", "warning", "stop"
        ]
        
        for line in lines:
            cleaned = self.clean_hook(line)
            if len(cleaned.split()) >= 4 and len(cleaned) < 120:
                # If contains viral words, return immediately
                if any(m in cleaned.lower() for m in viral_markers):
                    logger.debug(f"Extracted viral hook: '{cleaned}'")
                    return cleaned

        # Fallback to the first readable sentence
        fallback = self.clean_hook(lines[0])
        if len(fallback.split()) >= 3:
            return fallback
            
        return "This changed everything..."
