import datetime
from typing import List
from ai.subtitles.formatting.models import SubtitleSegment

class ASSFormatter:
    """
    Generates Advanced Substation Alpha (ASS) subtitles for styling and animation.
    """

    def _format_ass_time(self, seconds: float) -> str:
        """
        Formats seconds to ASS timestamp: H:MM:SS.cc
        """
        td = datetime.timedelta(seconds=seconds)
        total_seconds = int(td.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        secs = total_seconds % 60
        centis = int(td.microseconds / 10000)
        return f"{hours:1d}:{minutes:02d}:{secs:02d}.{centis:02d}"

    def generate_ass(self, segments: List[SubtitleSegment], style_name: str = "Default") -> str:
        """
        Generates basic ASS content.
        """
        header = [
            "[Script Info]",
            "Title: Zem Generated Subtitles",
            "ScriptType: v4.00+",
            "PlayResX: 1920",
            "PlayResY: 1080",
            "",
            "[V4+ Styles]",
            "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
            f"Style: {style_name},Arial,60,&H00FFFFFF,&H0000FFFF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,3,0,5,10,10,10,1",
            "",
            "[Events]",
            "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"
        ]
        
        events = []
        for seg in segments:
            start = self._format_ass_time(seg.start_time)
            end = self._format_ass_time(seg.end_time)
            events.append(f"Dialogue: 0,{start},{end},{style_name},,0,0,0,,{seg.text}")
            
        return "\n".join(header + events)
