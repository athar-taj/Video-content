import ffmpeg
import os
import random
import logging
from typing import Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class DurationTrimmer:
    """
    Handles video trimming, looping, and segment generation using FFmpeg.
    """
    
    def __init__(self, temp_dir: str = "assets/videos/temp"):
        self.temp_dir = Path(temp_dir)
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    def trim_video(self, input_path: str, duration: float, output_path: Optional[str] = None) -> str:
        """
        Cuts a random segment of the required duration from the input video.
        """
        if not output_path:
            output_path = str(self.temp_dir / f"trimmed_{os.path.basename(input_path)}")
            
        # Get input duration first
        probe = ffmpeg.probe(input_path)
        input_duration = float(probe['format']['duration'])
        
        if input_duration < duration:
            return self.loop_video(input_path, duration, output_path)
            
        # Select a random start point
        max_start = max(0, input_duration - duration)
        start_time = random.uniform(0, max_start)
        
        try:
            (
                ffmpeg
                .input(input_path, ss=start_time, t=duration)
                .output(output_path, c="copy") # Use stream copy for speed if possible
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )
            return output_path
        except ffmpeg.Error as e:
            logger.error(f"FFmpeg trim error: {e.stderr.decode()}")
            raise

    def loop_video(self, input_path: str, target_duration: float, output_path: str) -> str:
        """
        Loops the video until it reaches the target duration.
        """
        # Complex filter for looping in FFmpeg
        # Or just use -stream_loop
        try:
            (
                ffmpeg
                .input(input_path, stream_loop=-1) # Infinite loop
                .output(output_path, t=target_duration, c="copy")
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )
            return output_path
        except ffmpeg.Error as e:
            logger.error(f"FFmpeg loop error: {e.stderr.decode()}")
            raise
            
    def create_clip(self, input_path: str, start: float, end: float, output_path: str) -> str:
        """
        Creates a specific clip from start to end.
        """
        try:
            (
                ffmpeg
                .input(input_path, ss=start, to=end)
                .output(output_path, c="copy")
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )
            return output_path
        except ffmpeg.Error as e:
            logger.error(f"FFmpeg clip error: {e.stderr.decode()}")
            raise
