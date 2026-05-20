from typing import List, Dict, Any
from ai.subtitles.formatting.models import SubtitleSegment
from ai.subtitles.formatting.srt_formatter import SRTFormatter
from ai.subtitles.formatting.json_formatter import JSONFormatter
from ai.subtitles.formatting.ass_formatter import ASSFormatter
from ai.subtitles.formatting.karaoke_formatter import KaraokeFormatter

class SubtitleSerializer:
    """
    Serializes subtitle segments into various formats.
    """

    def __init__(self):
        self.srt_formatter = SRTFormatter()
        self.json_formatter = JSONFormatter()
        self.ass_formatter = ASSFormatter()
        self.karaoke_formatter = KaraokeFormatter()

    def serialize(self, segments: List[SubtitleSegment], format_type: str, **kwargs) -> str:
        """
        Serializes segments to the specified format.
        """
        if format_type.lower() == "srt":
            return self.srt_formatter.generate_srt(segments)
        elif format_type.lower() == "json":
            return self.json_formatter.generate_json(segments, metadata=kwargs.get("metadata"))
        elif format_type.lower() == "ass":
            return self.ass_formatter.generate_ass(segments)
        elif format_type.lower() == "karaoke":
            return self.karaoke_formatter.generate_karaoke_ass(segments)
        else:
            raise ValueError(f"Unsupported subtitle format: {format_type}")
