from typing import List
from ai.subtitles.timestamps.models import WordTimestamp, SubtitleSegment

class TimingOptimizer:
    """
    Optimizes subtitle timing for readability and retention (TikTok/Shorts style).
    """
    def __init__(
        self, 
        min_duration: float = 0.5, 
        max_duration: float = 3.0, 
        max_words_per_segment: int = 5,
        chars_per_second: int = 20
    ):
        self.min_duration = min_duration
        self.max_duration = max_duration
        self.max_words_per_segment = max_words_per_segment
        self.chars_per_second = chars_per_second

    def optimize_segments(self, words: List[WordTimestamp]) -> List[SubtitleSegment]:
        """
        Groups words into segments based on duration and readability rules.
        """
        segments = []
        current_words = []
        
        for i, word in enumerate(words):
            current_words.append(word)
            
            # Check if we should break here
            should_break = False
            
            # 1. Max words reached
            if len(current_words) >= self.max_words_per_segment:
                should_break = True
            
            # 2. Punctuation break (rough heuristic: word ends with . , ! ?)
            if word.word.strip().endswith(('.', ',', '!', '?')):
                should_break = True
                
            # 3. Next word has a significant gap
            if i < len(words) - 1:
                if words[i+1].start_time - word.end_time > 0.3:
                    should_break = True
            
            # 4. Duration limit
            duration = word.end_time - current_words[0].start_time
            if duration >= self.max_duration:
                should_break = True

            if should_break or i == len(words) - 1:
                # Create segment
                seg_text = " ".join([w.word for w in current_words])
                start = current_words[0].start_time
                end = current_words[-1].end_time
                
                # Ensure minimum duration
                if end - start < self.min_duration:
                    # Extend end time if possible, or just accept it
                    pass
                
                segments.append(SubtitleSegment(
                    segment_id=f"seg_{len(segments)}",
                    text=seg_text,
                    start_time=start,
                    end_time=end,
                    words=current_words,
                    duration=end - start
                ))
                current_words = []
                
        return segments
