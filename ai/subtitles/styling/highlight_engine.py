from typing import List
from ai.subtitles.styling.models import HighlightConfig
from ai.subtitles.formatting.models import SubtitleSegment

class HighlightEngine:
    """
    Generates highlighting effects for active words in a segment.
    """
    def __init__(self, config: HighlightConfig = HighlightConfig()):
        self.config = config

    def apply_highlight(self, word_text: str, is_active: bool) -> str:
        """
        Wraps word in ASS tags for highlighting.
        """
        if not is_active:
            return word_text
            
        if self.config.highlight_style == "active_color":
            return f"{{\\1c{self.config.active_color}}}{word_text}{{\\1c}}"
        
        if self.config.highlight_style == "scale":
            # ASS scale tags \fscx and \fscy
            scale = int(self.config.scale_factor * 100)
            return f"{{\\fscx{scale}\\fscy{scale}}}{word_text}{{\\fscx100\\fscy100}}"
            
        return word_text

    def generate_karaoke_line(self, segment: SubtitleSegment) -> str:
        """
        Generates a line with \k tags.
        """
        karaoke_text = ""
        current_time = segment.start_time
        for word in segment.words:
            duration_cs = int((word.end_time - word.start_time) * 100)
            gap_cs = int((word.start_time - current_time) * 100)
            if gap_cs > 0:
                karaoke_text += f"{{\\k{gap_cs}}}"
            
            karaoke_text += f"{{\\k{duration_cs}}}{word.word} "
            current_time = word.end_time
            
        return karaoke_text.strip()
