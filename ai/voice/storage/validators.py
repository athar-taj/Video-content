import os
from pathlib import Path
from typing import Tuple

class AudioValidator:
    """
    Validates audio files for quality and integrity.
    """
    
    @staticmethod
    def is_valid_audio(file_path: Path) -> Tuple[bool, str]:
        """Checks if the file exists and is not empty."""
        if not file_path.exists():
            return False, "File does not exist"
            
        if file_path.stat().st_size < 1024: # Minimum 1KB for a valid mp3
            return False, "File is too small or empty"
            
        # Optional: Add ffmpeg-based validation for corruption
        # try:
        #     ffmpeg.probe(str(file_path))
        # except ffmpeg.Error:
        #     return False, "Corrupted audio file"
            
        return True, "Valid"

    @staticmethod
    def validate_duration(duration: float, min_duration: float = 1.0) -> bool:
        return duration >= min_duration
