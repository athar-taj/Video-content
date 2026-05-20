import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class KaraokeRenderer:
    """Renders highlighted words and karaoke effects."""
    
    def generate_karaoke_line(self, words: List[Dict], highlight_color: str = "&H0000FFFF&") -> str:
        """
        Generate ASS karaoke tags for a line.
        words: [{"word": "Hello", "duration_ms": 300}, ...]
        """
        logger.info("Generating karaoke/highlight line.")
        
        line = ""
        for w in words:
            word_text = w.get("word", "")
            duration = w.get("duration_ms", 100) // 10  # ASS \k takes duration in centiseconds
            
            # Simple word-by-word karaoke fill: {\k30}Word
            # For active highlighting (change color then change back), it's more complex, 
            # but standard \K or \kf provides the sweeping fill.
            # Here we use a simple \kf (fill karaoke)
            line += f"{{\\kf{duration}}}{word_text} "
            
        return line.strip()
