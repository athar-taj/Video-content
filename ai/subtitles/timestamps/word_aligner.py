from typing import List
from ai.subtitles.timestamps.models import WordTimestamp
from ai.subtitles.timestamps.validators import TimestampValidator

class WordAligner:
    """
    Refines word alignments, fixes overlaps, and ensures consistency.
    """
    def __init__(self):
        self.validator = TimestampValidator()

    def refine_alignments(self, words: List[WordTimestamp]) -> List[WordTimestamp]:
        """
        Cleans up raw timestamps from Whisper.
        """
        if not words:
            return []
            
        # Ensure rendering safe (no overlaps, valid durations)
        refined = self.validator.ensure_rendering_safe(words)
        
        # Additional refinement: merge very close words if they are part of the same "thought"?
        # Or just ensure there are no gaps too small to be meaningful.
        
        return refined

    def fix_timing_mismatches(self, words: List[WordTimestamp], audio_duration: float) -> List[WordTimestamp]:
        """
        Ensures timestamps don't exceed audio duration.
        """
        fixed_words = []
        for word in words:
            if word.start_time >= audio_duration:
                # This shouldn't happen usually, but for safety
                continue
            
            new_word = word.model_copy()
            if new_word.end_time > audio_duration:
                new_word.end_time = audio_duration
                
            fixed_words.append(new_word)
        return fixed_words
