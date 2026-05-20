import logging
from typing import List, Optional, Dict
from ai.subtitles.styling.models import CaptionStyle
from ai.subtitles.styling.font_manager import FontManager
from ai.subtitles.styling.animation_engine import AnimationEngine
from ai.subtitles.styling.highlight_engine import HighlightEngine
from ai.subtitles.styling.ass_style_generator import ASSStyleGenerator
from ai.subtitles.styling.style_templates import STYLE_TEMPLATES
from ai.subtitles.formatting.models import SubtitleSegment

logger = logging.getLogger(__name__)

class CaptionStyleManager:
    """
    Orchestrates the caption styling and animation process.
    """
    def __init__(self):
        self.font_manager = FontManager()
        self.style_generator = ASSStyleGenerator()
        self.templates = STYLE_TEMPLATES

    def get_style(self, style_name: str) -> CaptionStyle:
        return self.templates.get(style_name, self.templates["reels_clean"])

    def generate_styled_ass(self, segments: List[SubtitleSegment], style_name: str = "reels_clean") -> str:
        """
        Generates a full ASS file with the selected style and animations.
        """
        style = self.get_style(style_name)
        header = self.style_generator.generate_header([style])
        
        # Engines
        animator = AnimationEngine(style.animation_config)
        highlighter = HighlightEngine(style.highlight_config) if style.highlight_config else None
        
        events = []
        for seg in segments:
            start = self._format_ass_time(seg.start_time)
            end = self._format_ass_time(seg.end_time)
            
            # Apply animations and highlights
            text = seg.text
            if highlighter and style.highlight_config and style.highlight_config.highlight_style == "karaoke":
                text = highlighter.generate_karaoke_line(seg)
            
            # Wrap in animation tags
            styled_text = animator.apply_to_text(text, seg.duration)
            
            events.append(f"Dialogue: 0,{start},{end},{style.style_name},,0,0,0,,{styled_text}")
            
        return header + "\n" + "\n".join(events)

    def _format_ass_time(self, seconds: float) -> str:
        import datetime
        td = datetime.timedelta(seconds=seconds)
        total_seconds = int(td.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        secs = total_seconds % 60
        centis = int(td.microseconds / 10000)
        return f"{hours:1d}:{minutes:02d}:{secs:02d}.{centis:02d}"
