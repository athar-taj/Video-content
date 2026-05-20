import ffmpeg
import logging
import os
from typing import Dict, Any

logger = logging.getLogger(__name__)

class MetadataExtractor:
    """
    Extracts technical metadata from video files using ffprobe.
    """
    
    @staticmethod
    def get_metadata(file_path: str) -> Dict[str, Any]:
        """
        Extracts resolution, duration, fps, codec, bitrate, aspect ratio, orientation, file size.
        """
        try:
            probe = ffmpeg.probe(file_path)
            video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
            
            if not video_stream:
                raise ValueError(f"No video stream found in {file_path}")
            
            width = int(video_stream['width'])
            height = int(video_stream['height'])
            
            # Resolution
            resolution = f"{width}x{height}"
            
            # Orientation
            if height > width:
                orientation = "vertical"
            elif width > height:
                orientation = "horizontal"
            else:
                orientation = "square"
            
            # FPS
            avg_frame_rate = video_stream.get('avg_frame_rate', '0/0')
            if '/' in avg_frame_rate:
                num, den = map(int, avg_frame_rate.split('/'))
                fps = num / den if den != 0 else 0
            else:
                fps = float(avg_frame_rate)
                
            # Duration
            duration = float(probe.get('format', {}).get('duration', 0))
            if duration == 0:
                duration = float(video_stream.get('duration', 0))
                
            # Bitrate and Codec
            bitrate = int(probe.get('format', {}).get('bit_rate', 0))
            codec = video_stream.get('codec_name', 'unknown')
            
            # Aspect Ratio (Simplified)
            aspect_ratio = f"{width}:{height}"
            
            return {
                "resolution": resolution,
                "width": width,
                "height": height,
                "fps": fps,
                "duration_seconds": duration,
                "bitrate": bitrate,
                "codec": codec,
                "orientation": orientation,
                "aspect_ratio": aspect_ratio,
                "file_size": os.path.getsize(file_path)
            }
        except Exception as e:
            logger.error(f"Metadata extraction failed for {file_path}: {e}")
            raise
