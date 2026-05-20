from rapidfuzz import fuzz
from typing import List
from shared.config.settings import settings
from shared.logging.logger import log

class DuplicateScriptDetector:
    """Detects near-duplicate scripts using fuzzy matching."""
    
    @staticmethod
    def calculate_similarity(text1: str, text2: str) -> float:
        """Returns similarity score between 0 and 100."""
        return fuzz.token_set_ratio(text1, text2)

    def is_too_similar(self, new_script: str, existing_scripts: List[str]) -> bool:
        """Checks if a script is too similar to a list of historical scripts."""
        for existing in existing_scripts:
            score = self.calculate_similarity(new_script, existing)
            if score >= settings.SIMILARITY_THRESHOLD:
                log.debug(f"Script duplicate detected: {score}% similarity")
                return True
        return False
