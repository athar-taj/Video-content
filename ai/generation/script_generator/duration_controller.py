import re

class DurationController:
    """Controls and estimates script duration based on word counts."""
    
    WORDS_PER_MINUTE = 150 # Average conversational speed for narration
    
    @classmethod
    def estimate_duration(cls, text: str) -> float:
        """Estimates duration in seconds."""
        word_count = len(re.findall(r'\w+', text))
        return (word_count / cls.WORDS_PER_MINUTE) * 60

    @classmethod
    def fits_duration(cls, text: str, target_sec: int, tolerance_pct: float = 0.15) -> bool:
        """Checks if the script is within acceptable duration bounds."""
        est = cls.estimate_duration(text)
        lower = target_sec * (1 - tolerance_pct)
        upper = target_sec * (1 + tolerance_pct)
        return lower <= est <= upper
