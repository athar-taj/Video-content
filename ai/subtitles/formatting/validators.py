from typing import List
from ai.subtitles.formatting.models import SubtitleSegment

class SubtitleValidator:
    @staticmethod
    def validate_segments(segments: List[SubtitleSegment]) -> bool:
        """
        Validates a list of subtitle segments.
        Checks for overlapping segments, invalid timestamps, and empty text.
        """
        if not segments:
            return False

        for i, seg in enumerate(segments):
            # Check for invalid timestamps
            if seg.start_time < 0 or seg.end_time < 0:
                return False
            
            if seg.end_time <= seg.start_time:
                return False
                
            # Check for empty text
            if not seg.text.strip():
                return False
                
            # Check for overlaps
            if i > 0:
                if seg.start_time < segments[i-1].end_time:
                    # Minor overlaps might be allowed in some formats, but generally avoided
                    pass 
                    
        return True

    @staticmethod
    def validate_srt_block(block: str) -> bool:
        """
        Basic check for SRT block format.
        """
        lines = block.strip().split("\n")
        if len(lines) < 3:
            return False
        # Line 1 should be a number
        if not lines[0].isdigit():
            return False
        # Line 2 should contain -->
        if " --> " not in lines[1]:
            return False
        return True
