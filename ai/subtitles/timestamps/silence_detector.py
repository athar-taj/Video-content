from typing import List, Tuple
from ai.subtitles.timestamps.models import WordTimestamp

class SilenceDetector:
    """
    Detects pauses between words to improve subtitle timing and support dramatic pacing.
    """
    def __init__(self, silence_threshold: float = 0.5):
        """
        silence_threshold: minimum gap in seconds to be considered a significant silence.
        """
        self.silence_threshold = silence_threshold

    def detect_pauses(self, words: List[WordTimestamp]) -> List[Tuple[float, float]]:
        """
        Returns a list of (start, end) tuples representing silent intervals.
        """
        pauses = []
        for i in range(len(words) - 1):
            gap = words[i+1].start_time - words[i].end_time
            if gap >= self.silence_threshold:
                pauses.append((words[i].end_time, words[i+1].start_time))
        return pauses

    def get_dramatic_pauses(self, words: List[WordTimestamp], threshold: float = 1.0) -> List[Tuple[float, float]]:
        """
        Detects longer pauses that might be intended for dramatic effect.
        """
        return [p for p in self.detect_pauses(words) if (p[1] - p[0]) >= threshold]
