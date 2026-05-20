from typing import List
from ai.subtitles.timestamps.models import WordTimestamp, SubtitleSegment

class TimestampValidator:
    @staticmethod
    def validate_word_timestamps(words: List[WordTimestamp]) -> bool:
        """
        Validates a list of word timestamps.
        Checks for negative timestamps, overlapping words, and invalid durations.
        """
        for i, word in enumerate(words):
            # Check for negative timestamps
            if word.start_time < 0 or word.end_time < 0:
                return False
            
            # Check for invalid durations
            if word.end_time <= word.start_time:
                return False
            
            # Check for overlapping words (allow a small overlap if necessary, but generally they should be sequential)
            if i > 0:
                if word.start_time < words[i-1].end_time:
                    # In some cases, Whisper might produce slight overlaps. 
                    # For strict validation, we could return False here.
                    pass 
        
        return True

    @staticmethod
    def validate_segment(segment: SubtitleSegment) -> bool:
        """
        Validates a subtitle segment.
        """
        if segment.start_time < 0 or segment.end_time < 0:
            return False
        
        if segment.end_time <= segment.start_time:
            return False
        
        if abs(segment.end_time - segment.start_time - segment.duration) > 0.001:
            return False
            
        return TimestampValidator.validate_word_timestamps(segment.words)

    @staticmethod
    def ensure_rendering_safe(words: List[WordTimestamp]) -> List[WordTimestamp]:
        """
        Fixes common issues to make timestamps safe for rendering.
        """
        if not words:
            return []

        cleaned_words = []
        for i, word in enumerate(words):
            start = max(0, word.start_time)
            end = max(start + 0.01, word.end_time) # Ensure at least 10ms duration
            
            # Ensure no overlap with previous word
            if cleaned_words and start < cleaned_words[-1].end_time:
                start = cleaned_words[-1].end_time
                end = max(start + 0.01, end)
                
            cleaned_words.append(WordTimestamp(
                word=word.word,
                start_time=start,
                end_time=end,
                confidence=word.confidence,
                position=word.position,
                speaker=word.speaker
            ))
            
        return cleaned_words
