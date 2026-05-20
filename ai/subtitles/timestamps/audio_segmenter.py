import os
import subprocess
from typing import List

class AudioSegmenter:
    """
    Handles audio preprocessing and segmentation for long narrations.
    """
    def __init__(self, temp_dir: str = "assets/subtitles/temp"):
        self.temp_dir = temp_dir
        os.makedirs(temp_dir, exist_ok=True)

    def preprocess_audio(self, audio_path: str) -> str:
        """
        Normalizes audio for better transcription (e.g., convert to 16kHz mono).
        """
        output_path = os.path.join(self.temp_dir, "normalized_" + os.path.basename(audio_path))
        # ffmpeg command for normalization
        cmd = [
            "ffmpeg", "-y", "-i", audio_path,
            "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le",
            output_path
        ]
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return output_path
        except subprocess.CalledProcessError as e:
            print(f"Error normalizing audio: {e.stderr.decode()}")
            return audio_path

    def split_audio(self, audio_path: str, segment_length: int = 30) -> List[str]:
        """
        Splits audio into smaller chunks for parallel processing if needed.
        """
        # For simplicity, we might just use the full file if it's not too long.
        # But this is where chunking logic would go.
        return [audio_path]
