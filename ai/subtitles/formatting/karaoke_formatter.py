from typing import List
from ai.subtitles.formatting.models import SubtitleSegment
from ai.subtitles.formatting.ass_formatter import ASSFormatter

class KaraokeFormatter(ASSFormatter):
    """
    Generates ASS subtitles with karaoke highlighting (\k tags).
    """

    def generate_karaoke_ass(self, segments: List[SubtitleSegment], style_name: str = "Default") -> str:
        header = [
            "[Script Info]",
            "Title: Zem Karaoke Subtitles",
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
            
            karaoke_text = ""
            current_time = seg.start_time
            for word in seg.words:
                duration_cs = int((word.end_time - word.start_time) * 100)
                gap_cs = int((word.start_time - current_time) * 100)
                if gap_cs > 0:
                    karaoke_text += f"{{\\k{gap_cs}}}"
                
                karaoke_text += f"{{\\k{duration_cs}}}{word.word} "
                current_time = word.end_time
                
            events.append(f"Dialogue: 0,{start},{end},{style_name},,0,0,0,,{karaoke_text.strip()}")
            
        return "\n".join(header + events)
