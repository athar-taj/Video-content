import datetime
from typing import List
from ai.subtitles.formatting.models import SubtitleSegment

class SRTFormatter:
    """
    Generates standard-compliant SRT subtitles.
    """

    def format_timestamp(self, seconds: float) -> str:
        """
        Formats seconds to SRT timestamp: HH:MM:SS,mmm
        """
        td = datetime.timedelta(seconds=seconds)
        total_seconds = int(td.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        secs = total_seconds % 60
        # Use microseconds to get milliseconds
        millis = int(td.microseconds / 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

    def generate_block(self, index: int, segment: SubtitleSegment) -> str:
        """
        Generates a single SRT subtitle block.
        """
        start = self.format_timestamp(segment.start_time)
        end = self.format_timestamp(segment.end_time)
        return f"{index}\n{start} --> {end}\n{segment.text}\n"

    def generate_srt(self, segments: List[SubtitleSegment]) -> str:
        """
        Generates the full SRT content from segments.
        """
        blocks = []
        for i, seg in enumerate(segments):
            blocks.append(self.generate_block(i + 1, seg))
        return "\n".join(blocks)
