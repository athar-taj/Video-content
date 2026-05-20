import re
from typing import List, Tuple
from rapidfuzz import fuzz, process
from ai.subtitles.timestamps.models import WordTimestamp

class TranscriptMatcher:
    """
    Compares original script vs transcription to repair alignment gaps and improve accuracy.
    """
    def __init__(self, fuzzy_threshold: int = 80):
        self.fuzzy_threshold = fuzzy_threshold

    def normalize_text(self, text: str) -> str:
        """
        Normalizes text for better matching: lowercase, remove punctuation.
        """
        text = text.lower()
        text = re.sub(r'[^\w\s]', '', text)
        return text.strip()

    def align_transcript(self, original_script: str, transcribed_words: List[WordTimestamp]) -> List[WordTimestamp]:
        """
        Aligns the original script with the transcribed words.
        Ensures the final words match the script while keeping the timing from transcription.
        """
        script_words = original_script.split()
        normalized_script_words = [self.normalize_text(w) for w in script_words]
        
        aligned_words = []
        trans_idx = 0
        
        for i, script_word in enumerate(script_words):
            norm_script = normalized_script_words[i]
            if not norm_script:
                continue

            # Look ahead in transcribed words for a match
            best_match_idx = -1
            best_score = 0
            
            # Search window: current trans_idx to trans_idx + 10
            for j in range(trans_idx, min(trans_idx + 10, len(transcribed_words))):
                norm_trans = self.normalize_text(transcribed_words[j].word)
                score = fuzz.ratio(norm_script, norm_trans)
                if score > self.fuzzy_threshold and score > best_score:
                    best_score = score
                    best_match_idx = j
            
            if best_match_idx != -1:
                # Found a match, use its timing
                match_word = transcribed_words[best_match_idx]
                aligned_words.append(WordTimestamp(
                    word=script_word, # Use original script word (with punctuation)
                    start_time=match_word.start_time,
                    end_time=match_word.end_time,
                    confidence=match_word.confidence,
                    position=i,
                    speaker=match_word.speaker
                ))
                trans_idx = best_match_idx + 1
            else:
                # No match found, interpolate timing if possible or use previous word's end
                start = aligned_words[-1].end_time if aligned_words else 0.0
                end = start + 0.2 # Default 200ms for missing words
                
                # If we have a next match, we could better interpolate, but for now:
                aligned_words.append(WordTimestamp(
                    word=script_word,
                    start_time=start,
                    end_time=end,
                    confidence=0.0,
                    position=i,
                    speaker=None
                ))
        
        return aligned_words
